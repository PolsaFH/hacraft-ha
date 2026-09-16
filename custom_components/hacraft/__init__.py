"""The HACraft integration.

Registers the hacraft/* websocket commands that the
HACraft Minecraft mod authenticates against Home Assistant's
own /api/websocket to use - see docs/PROTOCOL.md for the wire format.
"""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .websocket_api import async_register_commands

# "camera" backs the dynamically-created camera.hacraft_<camera_id>
# entities - see camera.py. Nothing else in this integration is a platform
# (the mod's own blocks aren't Home Assistant entities).
PLATFORMS: list[str] = ["camera"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HACraft from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    async_register_commands(hass)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a HACraft config entry.

    Note: Home Assistant's websocket_api has no async_unregister_command,
    so the hacraft/* commands stay registered for the life of
    the HA process even after the config entry is removed; any already-open
    mod connection isn't force-closed either. Acceptable for a
    single-instance integration like this one - noted so it isn't a
    surprise later if a "reload integration" workflow is added.
    """
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.pop(DOMAIN, None)
    return unload_ok
