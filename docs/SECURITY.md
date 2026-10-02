# HACraft security notes

HACraft stores people's Home Assistant access tokens and can switch lights,
open covers and stream camera pictures, so this is what it does - and does not -
protect against. Server admins should read the last section.

## Credentials

* Each player links their own Home Assistant with a long-lived access token,
  typed into the Home Server block's screen. There is no chat command for it, so
  it never lands in chat logs or command history.
* On the server the token is stored encrypted (AES-256-GCM) in
  `config/hacraft/players/<uuid>.json`. The key is `config/hacraft/server.key`,
  created owner-only. This stops a stray backup or an accidental `git add .`
  from leaking a live token. **It does not protect against someone with
  filesystem access to the server** - they have the key too.
* The token and full URL are never logged; only the host name is.

## What a client may ask the server to do

A modified client can send any packet, so the server re-checks everything:

* every packet that acts on a block is ignored unless the player is within
  `interactionRangeBlocks` of it, owns it (or was invited with `/ha invite`,
  or the owner ran `/ha access open`) and the block is in a loaded chunk;
* the Home Controller only forwards a short list of services
  (toggle / turn on / turn off / open, close and stop cover), and only for
  entities that were added to that controller;
* temperatures are clamped to the device's own `min_temp`/`max_temp`, volume and
  brightness to 0-100;
* service calls are rate limited per player (`serviceCallsPerSecond`) and camera
  frames per camera (`cameraMaxFramesPerSecond`, size capped by the packet);
* only entities the player exposed in the HACraft integration's own options can
  be seen or controlled - the integration refuses everything else on its side.

## Cameras on screens

A Home Sensor Screen bound to a `camera.*` entity shows its picture. The **server** downloads it from Home
Assistant's camera proxy with the owner's token (only for cameras the owner exposed to HACraft, every few
seconds, and only while a player is within 32 blocks) and sends it to every player near the screen. Anyone
who can see the screen can see the camera, so only bind cameras you are happy for visitors to look at.

## Network

The **server** opens the connection to Home Assistant, using the address the
player typed. On a public server that lets players make it connect to any host
the server can reach. Set `allowedHostSuffixes` in `config/hacraft-common.toml`
(for example `["homeassistant.local", "ui.nabu.casa"]`) to restrict it. Use
`https://` / `wss://` addresses when Home Assistant is reachable over the internet.

## Recommendations for server admins

1. Set `allowedHostSuffixes` if players you don't fully trust can join.
2. Keep `config/hacraft/` out of backups that leave the machine, or encrypt them.
3. Tell players to create a token for HACraft only and to expose only the
   entities they want in Minecraft (Settings -> Devices & Services -> HACraft ->
   Configure). Doors, locks and alarms are better left out.
