"""Tjenester til prisovervågning."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv, entity_registry as er

from .api import normalize_search
from .const import CONF_MODE, DOMAIN, MODE_WATCHLIST
from .watch import notify_targets
from .watchlist import WatchlistCoordinator

WATCH_SCHEMA = vol.Schema(
    {
        vol.Exclusive("entity_id", "what"): cv.entity_id,
        vol.Exclusive("query", "what"): cv.string,
        vol.Optional("name"): cv.string,
        vol.Required("price"): vol.All(vol.Coerce(float), vol.Range(min=0.01)),
        vol.Required("notify"): vol.All(cv.ensure_list, [cv.string], vol.Length(min=1)),
    }
)
UPDATE_SCHEMA = vol.Schema(
    {
        vol.Required("watch_id"): cv.string,
        vol.Optional("price"): vol.All(vol.Coerce(float), vol.Range(min=0.01)),
        vol.Optional("notify"): vol.All(cv.ensure_list, [cv.string], vol.Length(min=1)),
    }
)
UNWATCH_SCHEMA = vol.Schema(
    {
        vol.Exclusive("watch_id", "what"): cv.string,
        vol.Exclusive("entity_id", "what"): cv.entity_id,
    }
)


def _watchlist_entry(hass: HomeAssistant) -> ConfigEntry | None:
    return next(
        (e for e in hass.config_entries.async_entries(DOMAIN) if e.data.get(CONF_MODE) == MODE_WATCHLIST),
        None,
    )


async def async_get_watchlist(hass: HomeAssistant, create: bool = False) -> WatchlistCoordinator:
    """Overvågningslisten. Oprettes første gang, der overvåges noget."""
    entry = _watchlist_entry(hass)
    if entry is None and create:
        await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_IMPORT}, data={"watchlist": True})
        entry = _watchlist_entry(hass)
    coordinator = getattr(entry, "runtime_data", None) if entry else None
    if coordinator is None:
        raise ServiceValidationError("Prisovervågning er ikke sat op")
    return coordinator


def _source_coordinator(hass: HomeAssistant, entity_id: str):
    entity = er.async_get(hass).async_get(entity_id)
    entry = hass.config_entries.async_get_entry(entity.config_entry_id) if entity else None
    if entry is None or entry.domain != DOMAIN or entry.data.get(CONF_MODE) == MODE_WATCHLIST:
        raise ServiceValidationError(f"{entity_id} er ikke en Tilbudsjagt-vare eller -søgning")
    return entry, entry.runtime_data


def _check_targets(hass: HomeAssistant, targets: list[str]) -> list[str]:
    targets = [t.removeprefix("notify.") for t in targets]
    known = set(notify_targets(hass))
    if unknown := [t for t in targets if t not in known]:
        raise ServiceValidationError(f"Ukendt enhed: {', '.join(unknown)}")
    return targets


async def _async_watch(call: ServiceCall) -> ServiceResponse:
    hass = call.hass
    targets = _check_targets(hass, call.data["notify"])
    spec: dict[str, Any]
    if "entity_id" in call.data:
        entry, source = _source_coordinator(hass, call.data["entity_id"])
        spec = source.watch_spec()
        if not spec["slug"]:
            raise ServiceValidationError("Søg efter en vare før du opretter overvågning")
        name = call.data.get("name") or (source.query.strip().title() if source.is_search else entry.title)
    elif query := call.data.get("query", "").strip():
        spec = {"slug": normalize_search(query), "query": query, "filters": {}}
        name = call.data.get("name") or query.title()
    else:
        raise ServiceValidationError("Angiv en vare (query) eller en Tilbudsjagt-sensor (entity_id)")

    watchlist = await async_get_watchlist(hass, create=True)
    watch = await watchlist.async_add(name=name, price=call.data["price"], notify=targets, **spec)
    return {"watch_id": watch["id"], "name": watch["name"]}


async def _async_update(call: ServiceCall) -> None:
    hass = call.hass
    watchlist = await async_get_watchlist(hass)
    notify = _check_targets(hass, call.data["notify"]) if "notify" in call.data else None
    try:
        await watchlist.async_update_watch(call.data["watch_id"], call.data.get("price"), notify)
    except KeyError as err:
        raise ServiceValidationError("Overvågningen findes ikke") from err


async def _async_unwatch(call: ServiceCall) -> None:
    hass = call.hass
    watchlist = await async_get_watchlist(hass)
    watch_id = call.data.get("watch_id")
    if "entity_id" in call.data:
        _, source = _source_coordinator(hass, call.data["entity_id"])
        watch = watchlist.find(source.current_slug)
        watch_id = watch["id"] if watch else None
    if not watch_id:
        raise ServiceValidationError("Overvågningen findes ikke")
    try:
        await watchlist.async_remove(watch_id)
    except KeyError as err:
        raise ServiceValidationError("Overvågningen findes ikke") from err


def async_setup_services(hass: HomeAssistant) -> None:
    hass.services.async_register(
        DOMAIN, "watch", _async_watch, schema=WATCH_SCHEMA, supports_response=SupportsResponse.OPTIONAL
    )
    hass.services.async_register(DOMAIN, "update_watch", _async_update, schema=UPDATE_SCHEMA)
    hass.services.async_register(DOMAIN, "unwatch", _async_unwatch, schema=UNWATCH_SCHEMA)
