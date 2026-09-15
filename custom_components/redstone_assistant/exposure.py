"""Thin wrapper around Home Assistant's built-in entity exposure list.

Reuses the same per-entity "expose to X" list that already backs Assist and
the Google Assistant / Alexa cloud integrations
(``homeassistant.components.homeassistant.exposed_entities``), registering
``redstone_assistant`` as another consumer of it instead of building a
second entity picker UI. A user manages "what Minecraft can see" from the
same Settings -> Voice Assistants -> Expose screen they may already know.

This import could not be verified against a running Home Assistant install
from where this was written (see this repo's README for why) - if entities
never show up as exposed on your HA version, this is the first place to
check; the module path or function signature may have moved.
"""
from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

try:
    from homeassistant.components.homeassistant.exposed_entities import (
        async_should_expose as _ha_async_should_expose,
    )

    _EXPOSURE_AVAILABLE = True
except ImportError:  # pragma: no cover - defensive, see module docstring
    _EXPOSURE_AVAILABLE = False
    _LOGGER.warning(
        "Could not import homeassistant.components.homeassistant."
        "exposed_entities.async_should_expose - Redstone Assistant will "
        "treat every entity as NOT exposed (fail closed) until this is "
        "fixed. See the redstone-assistant-ha README for details."
    )


def async_should_expose(hass: HomeAssistant, entity_id: str) -> bool:
    """Whether entity_id has been exposed to the redstone_assistant "assistant".

    Fails closed: if the underlying Home Assistant API isn't available or
    raises, nothing is reported as exposed rather than everything.
    """
    if not _EXPOSURE_AVAILABLE:
        return False
    try:
        return bool(_ha_async_should_expose(hass, DOMAIN, entity_id))
    except Exception:  # noqa: BLE001 - defensive, see module docstring
        _LOGGER.debug("async_should_expose failed for %s", entity_id, exc_info=True)
        return False
