# HACraft for Home Assistant

[![Validate](https://github.com/PolsaFH/hacraft-ha/actions/workflows/validate.yml/badge.svg)](https://github.com/PolsaFH/hacraft-ha/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

The Home Assistant half of **HACraft**: a custom integration that lets the
[HACraft Minecraft mod](https://github.com/PolsaFH/ha-mc-mod) read and control the devices **you choose** to
share, from inside Minecraft - lights, thermostats, blinds, speakers, vacuums, sensors with live graphs, even
camera pictures on an in-game TV.

The integration is small on purpose: it adds a few commands to Home Assistant's own websocket API and keeps one
list - what Minecraft is allowed to see. The mod connects with an ordinary long-lived access token, exactly like
any other Home Assistant client.

## Installation

**HACS:** *HACS -> Integrations -> three dots -> Custom repositories*, add `https://github.com/PolsaFH/hacraft-ha`
as an *Integration*, install **HACraft** and restart Home Assistant.

**Manually:** copy `custom_components/hacraft` into your Home Assistant `custom_components` folder and restart.

Then:

1. *Settings -> Devices & Services -> Add integration -> HACraft* (a single confirmation step, nothing to fill in).
2. On the HACraft card press **Configure** and pick what Minecraft may see (see below).
3. Create a **long-lived access token** (your profile -> *Security*) and give it to the mod's Home Server block;
   the mod's README has the in-game steps.

## Choosing what Minecraft can see

**Configure** on the HACraft card opens HACraft's own picker (it is *not* the Voice assistants "Expose" screen -
Home Assistant does not let a custom integration add a tab there). Tick whole groups ("All lights", "All
cameras", ...) or individual devices. Anything not ticked is invisible and untouchable for the mod, even if a
player types the exact entity id in-game.

| Domain | Used for |
|---|---|
| `light`, `switch`, `input_boolean`, `fan` | Light Switch, Controller, Action, screens |
| `climate` | Thermostat |
| `cover` | Cover (blinds, garage doors, ...) |
| `media_player` | Media Player |
| `vacuum` | Vacuum Dock |
| `sensor`, `binary_sensor` | Sensor, Sensor Screen (text, graphs) |
| `script`, `scene`, `button` | Action block |
| `camera` | pictures on a Sensor Screen |

> **After updating the integration, open Configure again.** Domains added by a newer release (for example
> `media_player`, or `camera` in 0.5.0) are never ticked automatically, so the mod lists nothing for them until
> you do. Restart Home Assistant after updating the files, and make sure the integration is enabled - a
> disabled entry exposes nothing.

## Compatibility

| Integration | Mod | Notes |
|---|---|---|
| 0.5.x | 0.2.x, 0.3.x | recorded history for graphs, cameras, scripts, scenes, buttons and fans |
| 0.4.x | 0.2.x | works; graphs fill up live only and those extra domains are missing |

Needs Home Assistant 2024.1 or newer. Graph history needs the **recorder** integration (on by default).

## What it adds to Home Assistant

Commands on Home Assistant's own `/api/websocket` (details in [docs/PROTOCOL.md](docs/PROTOCOL.md)):

| Command | Purpose |
|---|---|
| `hacraft/list_entities` | the exposed entities and their state |
| `hacraft/subscribe_entities` | push state changes for the entities the mod follows |
| `hacraft/call_service` | run a service on one exposed entity |
| `hacraft/get_history` | recorded history of an exposed entity, evenly sampled (fills the mod's graphs) |
| `hacraft/camera_frame`, `hacraft/camera_removed` | pictures from Minecraft's Home Camera blocks, which appear as `camera.hacraft_<name>` |

Every command checks that the entity is exposed; the integration refuses everything else.

## Troubleshooting

* **The mod lists nothing for a device type** - tick it under *Configure* (see the note above), and check the
  integration card is enabled.
* **A graph starts empty** - the recorder must be running, and the integration must be 0.5.0 or newer.
* **Camera pictures do not show up** - tick the camera (or "All cameras") under *Configure*. The mod fetches
  pictures through Home Assistant's camera proxy with the player's token.
* **Home Assistant logs "unknown command: hacraft/..."** - the integration is older than the mod expects;
  update it and restart.

## Diagnostics

*Settings -> Devices & Services -> HACraft -> three dots -> Download diagnostics* gives a small file with the
integration and Home Assistant versions, whether the recorder is running, and how many entities of each domain
Minecraft can see. It holds counts only - no entity names, addresses or tokens - so it is safe to attach to a
bug report.

## Development

`custom_components/hacraft` is the integration; `tests/` holds tests for the pure helpers
(`python3 tests/test_history.py`, `python3 tests/test_summary.py`). The GitHub workflow runs `hassfest`, HACS validation and these tests on every
push and weekly. `docs/PROTOCOL.md` is the wire format; the mod repository has a copy that must stay in sync.

## License

[MIT](LICENSE)
