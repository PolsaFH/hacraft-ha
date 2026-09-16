"""Constants for the HACraft integration."""

DOMAIN = "hacraft"

CMD_LIST_ENTITIES = f"{DOMAIN}/list_entities"
CMD_SUBSCRIBE_ENTITIES = f"{DOMAIN}/subscribe_entities"
CMD_CALL_SERVICE = f"{DOMAIN}/call_service"

ERR_ENTITY_NOT_EXPOSED = "entity_not_exposed"
ERR_SERVICE_CALL_FAILED = "service_call_failed"
ERR_INVALID_CAMERA_ID = "invalid_camera_id"

# hacraft/camera_frame - one JPEG snapshot from an in-game Home Camera block.
# Registration is implicit: the first frame for a given camera_id creates
# camera.hacraft_<camera_id> (see camera.py); every frame after that just
# replaces the stored image and notifies that entity to refresh. There's no
# separate "register" command - keeping the mod side simpler (one command,
# no ordering to get right) mattered more than protocol purity here.
CMD_CAMERA_FRAME = f"{DOMAIN}/camera_frame"

# Dispatcher signal fired once, the first time a camera_id is ever seen this
# HA run, so camera.py can add the entity - see websocket_api.py.
SIGNAL_CAMERA_REGISTERED = f"{DOMAIN}_camera_registered"
# Per-camera dispatcher signal (suffixed with the camera_id) fired on every
# frame, registered vs not - the entity just re-reads the stored bytes.
SIGNAL_CAMERA_FRAME_PREFIX = f"{DOMAIN}_camera_frame_"

# Config entry options keys set in HACraftOptionsFlow (config_flow.py) - see
# exposure.py for how they're used together.
#
# OPT_EXPOSED_ENTITIES: individually-picked entity_ids (the fallback for
# anything not covered by an "expose all" domain toggle below).
OPT_EXPOSED_ENTITIES = "exposed_entities"
# OPT_EXPOSE_ALL_DOMAINS: domains (from KNOWN_DOMAINS) where the user picked
# "expose all" instead of hand-picking entities one by one - e.g. ticking
# "All lights" means every light.* entity is exposed, including ones added
# to Home Assistant later, with no need to reopen this options flow.
OPT_EXPOSE_ALL_DOMAINS = "expose_all_domains"

# Domains the current mod release actually understands. list_entities still
# reports every exposed entity regardless of domain (a future mod version
# might understand more without a Home Assistant-side change), but this is
# used to pre-filter noisy domains the mod block/GUI would just show as
# unusable, exactly like the mod's own DomainCapability enum - keep the two
# in sync, see docs/PROTOCOL.md. Also used to build the "expose all X"
# per-domain toggle list and to restrict the individual entity picker so it
# isn't cluttered with binary_sensor/etc HACraft can't use yet. sensor is
# read-only in the mod (shown as plain state text, e.g. a temperature
# sensor) - no service calls are ever made against it.
KNOWN_DOMAINS = {"light", "switch", "climate", "cover", "sensor"}

# Human-readable labels for KNOWN_DOMAINS, used by the "expose all" selector
# in HACraftOptionsFlow.
DOMAIN_LABELS = {
    "light": "All lights",
    "switch": "All switches",
    "climate": "All climate devices",
    "cover": "All covers",
    "sensor": "All sensors",
}
