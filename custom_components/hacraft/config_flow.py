"""Config flow for HACraft.

Home Assistant-side setup itself is a single confirmation step (see
async_step_user) - the Minecraft mod is what holds a URL and a long-lived
access token (entered in-game, in the Home Server block's GUI - see
hacraft-mod). What Minecraft is allowed to *see* is configured here though:
after adding the integration, open its "Configure" options and pick
entities with the entity picker in HACraftOptionsFlow below - see
exposure.py's module docstring for why this isn't the shared Settings ->
Voice Assistants -> Expose screen.
"""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import DOMAIN, DOMAIN_LABELS, KNOWN_DOMAINS, OPT_EXPOSE_ALL_DOMAINS, OPT_EXPOSED_ENTITIES


class HACraftConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the (trivial) HACraft config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(title="HACraft", data={})

        return self.async_show_form(step_id="user")

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> "HACraftOptionsFlow":
        return HACraftOptionsFlow()


class HACraftOptionsFlow(config_entries.OptionsFlow):
    """Pick which entities HACraft (and therefore the Minecraft mod) can see.

    This is HACraft's own exposure list, separate from Home Assistant's
    Assist/Google/Alexa exposure list - see exposure.py's module docstring
    for why. self.config_entry is populated automatically by the base
    OptionsFlow class - not set here, to avoid the deprecation warning
    older revisions of this file triggered by assigning it manually.
    """

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_entities = self.config_entry.options.get(OPT_EXPOSED_ENTITIES, [])
        current_all_domains = self.config_entry.options.get(OPT_EXPOSE_ALL_DOMAINS, [])
        schema = vol.Schema(
            {
                # Bulk option first: "expose all lights" etc, so a user with
                # many lights doesn't have to hand-pick every single one (and
                # future lights are covered automatically too, no need to
                # come back here). See exposure.py for how the two options
                # combine.
                vol.Optional(OPT_EXPOSE_ALL_DOMAINS, default=current_all_domains): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(value=domain, label=DOMAIN_LABELS[domain])
                            for domain in sorted(KNOWN_DOMAINS)
                        ],
                        multiple=True,
                        mode=selector.SelectSelectorMode.LIST,
                    )
                ),
                # Individual picker for anything not covered by a blanket
                # "expose all" above - e.g. just one of several switches.
                # Filtered to the domains the mod actually understands
                # (KNOWN_DOMAINS) so this isn't cluttered with every sensor/
                # binary_sensor/etc in the house.
                vol.Optional(OPT_EXPOSED_ENTITIES, default=current_entities): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=sorted(KNOWN_DOMAINS), multiple=True)
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
