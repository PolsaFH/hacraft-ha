"""HACraft camera platform.

One entity per in-game Home Camera block, fed by JPEG frames pushed over
the hacraft/camera_frame websocket command (see websocket_api.py and
docs/PROTOCOL.md for the wire format). There is no way to know ahead of
time how many camera blocks a player has placed, so entities are created
dynamically the first time a given camera_id shows up - not declared here
or in a config flow.
"""
from __future__ import annotations

import logging

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import slugify

from .const import DOMAIN, SIGNAL_CAMERA_FRAME_PREFIX, SIGNAL_CAMERA_REGISTERED

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up the HACraft camera platform.

    No cameras exist at HA startup - real entities are added on demand, the
    first time a camera_id shows up in a hacraft/camera_frame call (see
    websocket_api.py's handle_camera_frame, which fires SIGNAL_CAMERA_REGISTERED
    exactly once per camera_id per HA run). known_camera_ids also protects
    against a duplicate entity if the mod reconnects and re-sends a frame
    for a camera_id this platform already added.
    """
    domain_data = hass.data.setdefault(DOMAIN, {})
    known_camera_ids: set[str] = domain_data.setdefault("known_camera_ids", set())

    @callback
    def _add_camera(camera_id: str, friendly_name: str) -> None:
        if camera_id in known_camera_ids:
            return
        known_camera_ids.add(camera_id)
        async_add_entities([HACraftCamera(entry.entry_id, camera_id, friendly_name)])

    entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_CAMERA_REGISTERED, _add_camera)
    )

    # A camera_id that already sent its first frame before this platform
    # finished loading (e.g. the mod reconnected faster than HA finished
    # setting up camera.py after a restart) would otherwise be silently
    # dropped, since it already missed its one-time SIGNAL_CAMERA_REGISTERED -
    # catch those up now from whatever's already stored.
    for camera_id, data in domain_data.get("camera_frames", {}).items():
        _add_camera(camera_id, data.get("friendly_name", camera_id))


class HACraftCamera(Camera):
    """A single Home Camera block, shown as a Home Assistant camera entity.

    Push-only, still-image - there is no live video stream, just a JPEG
    snapshot pushed every few seconds (the interval is set on the block's
    own settings screen in-game). Comparable to a doorbell's snapshot
    camera rather than a continuous RTSP feed.
    """

    _attr_has_entity_name = False
    _attr_should_poll = False

    def __init__(self, entry_id: str, camera_id: str, friendly_name: str) -> None:
        super().__init__()
        self._camera_id = camera_id
        self._attr_unique_id = f"{entry_id}_camera_{camera_id}"
        self._attr_name = f"HACraft {friendly_name}"
        # _attr_suggested_object_id turned out NOT to be enough on its own -
        # in practice this platform's entities still ended up named from
        # _attr_name ("HACraft Camera" for every camera whose friendly name
        # was left at the default "Camera"), so every camera placed in-game
        # collided on the same slug and Home Assistant appended _2/_3/_4
        # rather than using each camera's own id - four cameras all placed
        # for testing this session ended up as camera.hacraft_camera,
        # _camera_2, _camera_3, _camera_4, none of them named after their
        # actual camera_id. Setting entity_id directly is unambiguous and
        # matches docs/PROTOCOL.md's documented camera.hacraft_<camera_id>
        # shape regardless of what friendly_name the player chose.
        self.entity_id = f"camera.{DOMAIN}_{slugify(camera_id)}"

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, f"{SIGNAL_CAMERA_FRAME_PREFIX}{self._camera_id}", self._handle_new_frame
            )
        )

    @callback
    def _handle_new_frame(self, image_bytes: bytes) -> None:
        # The frontend re-fetches the image on demand (async_camera_image
        # below) rather than being pushed the bytes directly - this just
        # tells any open camera card/history entry that a new frame exists.
        self.async_write_ha_state()

    async def async_camera_image(self, width: int | None = None, height: int | None = None) -> bytes | None:
        data = self.hass.data.get(DOMAIN, {}).get("camera_frames", {}).get(self._camera_id)
        return data["image"] if data else None
