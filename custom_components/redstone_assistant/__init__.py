"""The Redstone Assistant integration.

Registers the redstone_assistant/* websocket commands that the
Redstone Assistant Minecraft mod authenticates against Home Assistant's
own /api/websocket to use - see docs/PROTOCOL.md for the wire format.
"""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .websocket_api import async_register_commands

PLATFORMS: list[str] = []


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Redstone Assistant from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    async_register_commands(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Redstone Assistant config entry.

    Note: Home Assistant's websocket_api has no async_unregister_command,
    so the redstone_assistant/* commands stay registered for the life of
    the HA process even after the config entry is removed; any already-open
    mod connection isn't force-closed either. Acceptable for a
    single-instance integration like this one - noted so it isn't a
    surprise later if a "reload integration" workflow is added.
    """
    hass.data.pop(DOMAIN, None)
    return True
