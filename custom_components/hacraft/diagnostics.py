"""Diagnostics download (Settings -> Devices & Services -> HACraft -> three dots -> Download diagnostics)."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration

from .const import CAMERA_ENTITY_PREFIX, DOMAIN
from .summary import summarize_exposure


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, Any]:
    """Counts only - no entity ids, tokens or addresses - so the file is safe to attach to an issue."""
    integration = await async_get_integration(hass, DOMAIN)
    states = hass.states.async_all()
    cameras = [s.entity_id for s in states if s.entity_id.startswith(CAMERA_ENTITY_PREFIX)]
    return {
        "integration_version": str(integration.version),
        "home_assistant_version": hass.config.version,
        "recorder_loaded": "recorder" in hass.config.components,
        "entry_state": entry.state.value,
        "exposure": summarize_exposure(entry.options, [s.entity_id for s in states]),
        "minecraft_cameras": len(cameras),
    }
