"""Config flow for HACraft.

There is nothing to configure on the Home Assistant side - this integration
only registers websocket commands. The Minecraft mod is what holds a URL
and a long-lived access token (entered in-game, in the Home Server block's
GUI - see hacraft-mod). This flow is a single confirmation step
that just turns the integration on, single-instance-only.
"""
from __future__ import annotations

from typing import Any

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN


class HACraftConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the (trivial) HACraft config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(title="HACraft", data={})

        return self.async_show_form(step_id="user")
