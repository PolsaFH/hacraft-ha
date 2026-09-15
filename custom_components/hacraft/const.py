"""Constants for the HACraft integration."""

DOMAIN = "hacraft"

CMD_LIST_ENTITIES = f"{DOMAIN}/list_entities"
CMD_SUBSCRIBE_ENTITIES = f"{DOMAIN}/subscribe_entities"
CMD_CALL_SERVICE = f"{DOMAIN}/call_service"

ERR_ENTITY_NOT_EXPOSED = "entity_not_exposed"
ERR_SERVICE_CALL_FAILED = "service_call_failed"

# Config entry options key holding the list of entity_ids the user picked in
# HACraftOptionsFlow (config_flow.py) - see exposure.py for how it's used.
OPT_EXPOSED_ENTITIES = "exposed_entities"

# Domains the current mod release actually understands. list_entities still
# reports every exposed entity regardless of domain (a future mod version
# might understand more without a Home Assistant-side change), but this is
# used to pre-filter noisy domains the mod block/GUI would just show as
# unusable, exactly like the mod's own DomainCapability enum - keep the two
# in sync, see docs/PROTOCOL.md.
KNOWN_DOMAINS = {"light", "switch", "climate", "cover"}
