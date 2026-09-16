# HACraft wire protocol

This is the source of truth for the commands exchanged between the mod
(`HaConnection`, in this repo) and the Home Assistant custom_component
(`hacraft/websocket_api.py`, in `hacraft-ha`). If you
change one side, update this file and the other repo's copy in the same PR -
a mismatched pair should fail loudly, not silently misbehave.

## Why this shape

We register our commands on Home Assistant's **existing, already-authenticated
websocket connection** (`/api/websocket`) via
`homeassistant.components.websocket_api.async_register_command`, rather than
standing up a second raw socket. That means every message follows HA's own
websocket API conventions - flat top-level fields, not a custom nested
envelope - because we're commands *on* that connection, not a separate
protocol layered under it. Concretely: the mod authenticates to
`/api/websocket` with a player's long-lived access token exactly like any
other HA client (`auth_required` -> `auth` -> `auth_ok`), then sends our
`hacraft/*` command types on top.

## Handshake

Standard HA auth, nothing custom:

```json
{"type": "auth_required"}
```
```json
{"type": "auth", "access_token": "<long-lived token>"}
```
```json
{"type": "auth_ok", "ha_version": "2025.x.x"}
```
(or `{"type": "auth_invalid", "message": "..."}`, which the mod surfaces
verbatim in the Home Server block's GUI as a connect error.)

## `hacraft/list_entities`

Request:
```json
{"id": 2, "type": "hacraft/list_entities"}
```

Result - only entities exposed to the `hacraft` "assistant" via
Home Assistant's existing Settings -> Voice Assistants -> Expose screen
(see `exposed_entities.py` in the HA repo):

```json
{"id": 2, "type": "result", "success": true, "result": {"entities": [
  {"entity_id": "light.kitchen", "domain": "light", "friendly_name": "Kitchen",
   "state": "on", "attributes": {"brightness": 180}},
  {"entity_id": "climate.living_room", "domain": "climate", "friendly_name": "Living Room",
   "state": "heat", "attributes": {"current_temperature": 21.4, "target_temperature": 22}}
]}}
```

## `hacraft/subscribe_entities`

Request:
```json
{"id": 3, "type": "hacraft/subscribe_entities", "entity_ids": ["light.kitchen"]}
```

Ack:
```json
{"id": 3, "type": "result", "success": true, "result": null}
```

Push events on that same `id`, for as long as the connection is open:
```json
{"id": 3, "type": "event", "event":
  {"entity_id": "light.kitchen", "domain": "light", "friendly_name": "Kitchen",
   "state": "off", "attributes": {}}}
```

Re-sending `subscribe_entities` with a new `entity_ids` list replaces the
previous subscription for that connection (the mod does this every time a
block is bound/unbound, sending the full current set rather than diffing).

## `hacraft/call_service`

Generic across domains - adding climate/cover controls costs nothing here:

```json
{"id": 4, "type": "hacraft/call_service",
 "domain": "light", "service": "toggle", "entity_id": "light.kitchen"}
```
```json
{"id": 5, "type": "hacraft/call_service",
 "domain": "climate", "service": "set_temperature",
 "entity_id": "climate.living_room", "data": {"temperature": 21}}
```

Result:
```json
{"id": 4, "type": "result", "success": true, "result": null}
```

## `hacraft/camera_frame`

One JPEG snapshot from an in-game Home Camera block. Unlike every other
command here, this one is also implicitly a registration: the first time a
given `camera_id` is seen (per Home Assistant run), the integration creates
a `camera.hacraft_<camera_id>` entity for it; every call after that just
replaces the stored frame and notifies that entity to refresh. There's
deliberately no separate `register_camera` command - one command with no
ordering to get right beats two with a "did I register yet" state machine
on the mod side.

`camera_id` must be 1-32 lowercase letters/digits/underscores (sanitized
client-side in the block's settings screen before it's ever sent).
`friendly_name` is free text, shown as `HACraft <friendly_name>` in Home
Assistant. `image_base64` is a base64-encoded JPEG - kept as raw bytes over
the Minecraft-side network packet and only base64-encoded right before this
call, since that's the one hop that actually needs a JSON-safe encoding.

```json
{"id": 6, "type": "hacraft/camera_frame",
 "camera_id": "front_door", "friendly_name": "Front Door",
 "image_base64": "/9j/4AAQSkZJRgABAQAAAQABAAD..."}
```

Result echoes back the entity_id it resolved to, purely so the mod's
settings screen can show the player where to find it in Home Assistant:

```json
{"id": 6, "type": "result", "success": true, "result": {"entity_id": "camera.hacraft_front_door"}}
```

The mod re-sends this on its own schedule (the interval is set on the
camera block's settings screen, a few seconds by default) for as long as
that camera is enabled and its owner is online - there's no separate
subscribe/unsubscribe step like `hacraft/subscribe_entities` uses, since the
mod is the one deciding when a new frame exists, not Home Assistant.

## Errors

Any command can fail with HA's normal result-error shape:

```json
{"id": 4, "type": "result", "success": false,
 "error": {"code": "entity_not_exposed", "message": "light.kitchen is not exposed to HACraft"}}
```

Known `code`s the integration should use consistently: `entity_not_exposed`,
`entity_not_found`, `invalid_domain`, `service_call_failed`, `invalid_camera_id`.

## Compatibility

There's no separate `protocol_version` handshake message - compatibility
rides on Home Assistant's own `manifest.json` version pin on the
`hacraft` integration and the mod's own `mod_version`. If a
breaking change to any command shape above is needed, bump both repos'
minor version together and note it in both changelogs; this file's git
history is the changelog for the wire format itself.
