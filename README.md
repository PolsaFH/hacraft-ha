# HACraft (Home Assistant integration)

A custom_component that lets the [HACraft Minecraft mod](https://github.com/filiphjelmeland/hacraft-mod)
connect to your Home Assistant instance and control the entities you choose
to expose to it - see the mod's README for the in-game setup flow.

## Status

Phase 1 - confirmed working against a real Home Assistant instance and a
real running Minecraft mod build: the config flow, websocket auth, and
`hacraft/*` commands all work end to end. The entity-exposure mechanism was
corrected after real-world testing - see "What's verified" below.

## Installation

Via [HACS](https://hacs.xyz/): add this repository as a custom repository
(Integrations), then install "HACraft" and restart Home
Assistant. Manually: copy `custom_components/hacraft` into your
Home Assistant `custom_components` folder and restart.

Then: Settings -> Devices & Services -> Add Integration -> "HACraft"
(there's nothing to fill in - it's a single confirmation step,
see `config_flow.py`'s docstring for why). Finally, pick the entities you
want Minecraft to see: find the HACraft integration card on that same
Settings -> Devices & Services page and click **Configure** - that opens
HACraft's own entity picker (not the Voice Assistants -> Expose screen,
see "What's verified" below for why). Anything not picked there is
invisible to the mod, even if a player types its exact entity_id in-game.

## What this integration does

Registers three commands on Home Assistant's own `/api/websocket`
connection (not a second socket - see `docs/PROTOCOL.md`):
`hacraft/list_entities`, `hacraft/subscribe_entities`,
`hacraft/call_service`. The mod authenticates to that same
`/api/websocket` endpoint with a normal long-lived access token, exactly
like any other Home Assistant client, then issues these on top.

Entity visibility is HACraft's own list, picked via its Options flow (the
"Configure" button on its integration card) and stored on the config
entry - see `exposure.py` and `config_flow.py`.

## What's verified vs. not

- **Verified against a real Home Assistant instance**: the config flow
  (single confirmation step), the integration loading successfully, and
  the mod connecting over `/api/websocket` with a long-lived access token
  and getting `auth_ok`.
- **Corrected after real-world testing**: the original design reused Home
  Assistant's built-in Settings -> Voice Assistants -> Expose screen (the
  one behind Assist/Google Assistant/Alexa) for entity visibility, on the
  assumption that a third-party integration could register itself there as
  another "assistant" tab. That assumption was wrong - that screen's tabs
  are hardcoded in Home Assistant's own frontend to
  `conversation`/`cloud.alexa`/`cloud.google_assistant`; "HACraft" never
  appeared as an option no matter how the integration was installed or set
  up. Fixed by giving HACraft its own Options flow entity picker instead
  (`config_flow.py`'s `HACraftOptionsFlow`, backed by
  `homeassistant.helpers.selector.EntitySelector` - a long-stable, widely
  used HA API, unlike the internal `exposed_entities` module this replaces).
- **Not yet verified**: the `websocket_api.ActiveConnection`/
  `connection.subscriptions` subscription-cleanup pattern in
  `websocket_api.py`, and the `Event[EventStateChangedData]` typed-event
  annotation, haven't specifically been exercised by a long-running
  `subscribe_entities` session yet (list_entities and call_service have).
  If live state updates don't reach the mod, `websocket_api.py` is the
  first place to check.

## License

Not yet chosen - see the architecture plan this was built from. Add a
`LICENSE` file before the first public release (GPL-3.0 is the common
convention for HACS integrations, if you want a default to start from).
