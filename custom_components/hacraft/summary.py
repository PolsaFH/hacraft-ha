"""Pure helpers for the diagnostics download (kept free of Home Assistant imports so tests can run without it)."""
from __future__ import annotations

from collections import Counter
from typing import Iterable, Mapping


def summarize_exposure(options: Mapping, entity_ids: Iterable[str]) -> dict:
    """How many entities of each domain the mod can see, given the config entry options.

    Entity ids themselves are left out on purpose: a diagnostics file gets attached to public issues, and the
    names of someone's devices are nobody else's business.
    """
    expose_all = set(options.get("expose_all_domains", []))
    picked = set(options.get("exposed_entities", []))
    counts: Counter = Counter()
    for entity_id in entity_ids:
        domain = entity_id.split(".", 1)[0]
        if domain in expose_all or entity_id in picked:
            counts[domain] += 1
    return {
        "expose_all_domains": sorted(expose_all),
        "individually_picked": len(picked),
        "visible_to_mod_by_domain": dict(sorted(counts.items())),
        "visible_to_mod_total": sum(counts.values()),
    }
