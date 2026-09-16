"""HACraft's commands on Home Assistant's own websocket API.

Registered on HA's existing, already-authenticated `/api/websocket`
connection (`websocket_api.async_register_command`) rather than a second
raw socket, so we get HA's auth/TLS/session handling for free - see
docs/PROTOCOL.md (and the matching copy in hacraft-mod) for the
full wire format and the reasoning.
"""
from __future__ import annotations

import base64
import logging
import re

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, State, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_state_change_event

from .const import (
    CMD_CALL_SERVICE,
    CMD_CAMERA_FRAME,
    CMD_LIST_ENTITIES,
    CMD_SUBSCRIBE_ENTITIES,
    DOMAIN,
    ERR_ENTITY_NOT_EXPOSED,
    ERR_INVALID_CAMERA_ID,
    ERR_SERVICE_CALL_FAILED,
    SIGNAL_CAMERA_FRAME_PREFIX,
    SIGNAL_CAMERA_REGISTERED,
)
from .exposure import async_should_expose

_CAMERA_ID_RE = re.compile(r"^[a-z0-9_]{1,32}$")

_LOGGER = logging.getLogger(__name__)


def _serialize_state(state: State) -> dict:
    return {
        "entity_id": state.entity_id,
        "domain": state.domain,
        "friendly_name": state.name,
        "state": state.state,
        "attributes": dict(state.attributes),
    }


@websocket_api.websocket_command(
    {
        vol.Required("type"): CMD_LIST_ENTITIES,
    }
)
@websocket_api.async_response
async def handle_list_entities(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict) -> None:
    """List every entity exposed to HACraft."""
    entities = [
        _serialize_state(state)
        for state in hass.states.async_all()
        if async_should_expose(hass, state.entity_id)
    ]
    connection.send_result(msg["id"], {"entities": entities})


@websocket_api.websocket_command(
    {
        vol.Required("type"): CMD_SUBSCRIBE_ENTITIES,
        vol.Required("entity_ids"): [cv.entity_id],
    }
)
@websocket_api.async_response
async def handle_subscribe_entities(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict) -> None:
    """Push state_changed-style events for the given entities to this connection.

    Re-sending this command with a new entity_ids list replaces any
    previous subscription registered under the same message id - the mod
    always sends its full current subscription set rather than diffing.
    """
    entity_ids = set(msg["entity_ids"])

    @callback
    def _forward_state(event: Event[EventStateChangedData]) -> None:
        new_state = event.data["new_state"]
        if new_state is None or new_state.entity_id not in entity_ids:
            return
        if not async_should_expose(hass, new_state.entity_id):
            return
        connection.send_message(
            websocket_api.messages.event_message(msg["id"], _serialize_state(new_state))
        )

    if msg["id"] in connection.subscriptions:
        connection.subscriptions.pop(msg["id"])()

    remove_listener = async_track_state_change_event(hass, list(entity_ids), _forward_state)
    connection.subscriptions[msg["id"]] = remove_listener
    connection.send_result(msg["id"])


@websocket_api.websocket_command(
    {
        vol.Required("type"): CMD_CALL_SERVICE,
        vol.Required("domain"): str,
        vol.Required("service"): str,
        vol.Required("entity_id"): cv.entity_id,
        vol.Optional("data"): dict,
    }
)
@websocket_api.async_response
async def handle_call_service(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict) -> None:
    """Call a Home Assistant service on one exposed entity."""
    entity_id = msg["entity_id"]
    if not async_should_expose(hass, entity_id):
        connection.send_error(
            msg["id"], ERR_ENTITY_NOT_EXPOSED, f"{entity_id} is not exposed to HACraft"
        )
        return

    service_data = dict(msg.get("data", {}))
    service_data["entity_id"] = entity_id

    try:
        await hass.services.async_call(msg["domain"], msg["service"], service_data, blocking=True)
    except Exception as err:  # noqa: BLE001 - surfaced to the mod as a call_service error, not a crash
        _LOGGER.debug("call_service failed for %s.%s on %s", msg["domain"], msg["service"], entity_id, exc_info=True)
        connection.send_error(msg["id"], ERR_SERVICE_CALL_FAILED, str(err))
        return

    connection.send_result(msg["id"])


@websocket_api.websocket_command(
    {
        vol.Required("type"): CMD_CAMERA_FRAME,
        vol.Required("camera_id"): str,
        vol.Required("friendly_name"): str,
        vol.Required("image_base64"): str,
    }
)
@websocket_api.async_response
async def handle_camera_frame(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict) -> None:
    """Store the latest snapshot for one in-game camera block and push it live.

    Creates the camera.hacraft_<camera_id> entity the first time this
    camera_id is seen this HA run (see camera.py's dispatcher listener);
    every call after that just replaces the stored frame and notifies that
    entity to refresh. There's no separate registration step - see
    CMD_CAMERA_FRAME's comment in const.py for why.
    """
    camera_id = msg["camera_id"]
    if not _CAMERA_ID_RE.match(camera_id):
        connection.send_error(
            msg["id"], ERR_INVALID_CAMERA_ID,
            "camera_id must be 1-32 lowercase letters, digits or underscores",
        )
        return

    try:
        image_bytes = base64.b64decode(msg["image_base64"], validate=True)
    except (base64.binascii.Error, ValueError):
        connection.send_error(msg["id"], ERR_INVALID_CAMERA_ID, "image_base64 is not valid base64")
        return

    domain_data = hass.data.setdefault(DOMAIN, {})
    frames = domain_data.setdefault("camera_frames", {})
    is_new = camera_id not in frames
    frames[camera_id] = {"image": image_bytes, "friendly_name": msg["friendly_name"]}

    if is_new:
        async_dispatcher_send(hass, SIGNAL_CAMERA_REGISTERED, camera_id, msg["friendly_name"])
    async_dispatcher_send(hass, f"{SIGNAL_CAMERA_FRAME_PREFIX}{camera_id}", image_bytes)

    connection.send_result(msg["id"], {"entity_id": f"camera.{DOMAIN}_{camera_id}"})


def async_register_commands(hass: HomeAssistant) -> None:
    """Register every hacraft/* websocket command."""
    websocket_api.async_register_command(hass, handle_list_entities)
    websocket_api.async_register_command(hass, handle_subscribe_entities)
    websocket_api.async_register_command(hass, handle_call_service)
    websocket_api.async_register_command(hass, handle_camera_frame)
