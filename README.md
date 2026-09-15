# HACraft (Home Assistant integration)

A custom_component that lets the [HACraft Minecraft mod](https://github.com/filiphjelmeland/hacraft-mod)
connect to your Home Assistant instance and control the entities you choose
to expose to it - see the mod's README for the in-game setup flow.

## Status

Phase 1 - freshly scaffolded, **not yet run against a real Home Assistant
instance.** See "What's verified" below.

## Installation

Via [HACS](https://hacs.xyz/): add this repository as a custom repository
(Integrations), then install "HACraft" and restart Home
Assistant. Manually: copy `custom_components/hacraft` into your
Home Assistant `custom_components` folder and restart.

Then: Settings -> Devices & Services -> Add Integration -> "HACraft"
(there's nothing to fill in - it's a single confirmation step,
see `config_flow.py`'s docstring for why). Finally, expose the entities you
want Minecraft to see: Settings -> Voice Assistants -> Expose -> (assistant
dropdown) -> HACraft, same screen used by Assist/Google/Alexa.

## What this integration does

Registers three commands on Home Assistant's own `/api/websocket`
connection (not a second socket - see `docs/PROTOCOL.md`):
`hacraft/list_entities`, `hacraft/subscribe_entities`,
`hacraft/call_service`. The mod authenticates to that same
`/api/websocket` endpoint with a normal long-lived access token, exactly
like any other Home Assistant client, then issues these on top.

Entity visibility reuses Home Assistant's existing per-entity exposure list
(the same one behind Assist/Google/Alexa) rather than a second picker UI -
see `exposure.py`.

## What's verified vs. not

This was written and reviewed carefully against documented Home Assistant
integration conventions, but **could not be run against a live Home
Assistant instance or even have `homeassistant` importable** in the
environment it was built in (installing the `homeassistant` PyPI package
timed out - it's a large package with a lot of transitive dependencies).
Concretely:

- Verified: every `.py` file passes `python3 -m py_compile` (syntax is
  valid Python).
- **Not verified**: the exact import path
  `homeassistant.components.homeassistant.exposed_entities.async_should_expose`
  in `exposure.py`, the `websocket_api.ActiveConnection`/
  `connection.subscriptions` pattern in `websocket_api.py`, and the
  `Event[EventStateChangedData]` typed-event annotation all reflect
  documented/observed Home Assistant core conventions as of when this was
  written, but none of them were checked against an actual installed
  `homeassistant` package. If setup fails on your HA version, `exposure.py`
  and `websocket_api.py` are the two most likely places - both fail
  defensively (entities report as not-exposed rather than crashing) if the
  exposure import is wrong, but a signature mismatch in the websocket
  command decorators would surface as a setup error worth reading closely.

## License

Not yet chosen - see the architecture plan this was built from. Add a
`LICENSE` file before the first public release (GPL-3.0 is the common
convention for HACS integrations, if you want a default to start from).
