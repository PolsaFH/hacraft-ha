"""HACraft's own entity exposure list.

Earlier versions of this integration tried to reuse Home Assistant's
built-in "expose to X" list
(``homeassistant.components.homeassistant.exposed_entities``), the same one
behind Assist and the Google Assistant / Alexa cloud integrations, instead
of building a second entity picker. That doesn't actually work: Home
Assistant's own frontend hardcodes the tabs on Settings -> Voice Assistants
-> Expose to conversation / cloud.alexa / cloud.google_assistant - a
third-party custom_component has no way to add itself as a selectable tab
there, so a user could never actually turn on exposure to "hacraft" through
that screen even though the backend call would silently accept the
assistant name. Confirmed against a live Home Assistant instance (the
Expose screen only ever shows "Assist" and "Google Assistant" - never
"HACraft", no matter how the integration is installed or set up).

HACraft now keeps its own exposure list instead, picked via this
integration's own Options flow (see config_flow.py) and stored in the
config entry's options under OPT_EXPOSED_ENTITIES.
"""
from __future__ import annotations

from homeassistant.core import HomeAssistant

from .const import DOMAIN, OPT_EXPOSE_ALL_DOMAINS, OPT_EXPOSED_ENTITIES


def async_should_expose(hass: HomeAssistant, entity_id: str) -> bool:
    """Whether entity_id was picked in HACraft's own options flow.

    Two ways an entity ends up exposed: it was individually picked
    (OPT_EXPOSED_ENTITIES), or its whole domain has "expose all" turned on
    (OPT_EXPOSE_ALL_DOMAINS) - the latter also covers entities added to
    Home Assistant after this was last configured, with no need to reopen
    the options flow. Fails closed: no config entry, or nothing picked
    yet, means nothing is reported as exposed.
    """
    entries = hass.config_entries.async_entries(DOMAIN)
    if not entries:
        return False
    # manifest.json sets single_config_entry: true, so there is only ever
    # one entry - no need to figure out "which one".
    options = entries[0].options
    domain = entity_id.split(".", 1)[0]
    if domain in options.get(OPT_EXPOSE_ALL_DOMAINS, []):
        return True
    return entity_id in options.get(OPT_EXPOSED_ENTITIES, [])
