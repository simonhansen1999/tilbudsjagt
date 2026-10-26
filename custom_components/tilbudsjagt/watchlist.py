"""Overvågningslisten: alle prisovervågninger samlet ét sted."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from typing import Any
import uuid

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .api import Offer, TilbudsugenError, async_fetch_offers, normalize_search, select_offers, words
from .const import AUTO, DEFAULTS, DOMAIN, NEW_DEFAULTS
from .watch import describe, kr

_LOGGER = logging.getLogger(__name__)
_UNITS = {"ltr": "l", "kg": "kg", "stk": "stk"}


@dataclass
class WatchState:
    """En overvågning og hvad den har fundet ved seneste hentning."""

    watch: dict[str, Any]
    hits: list[Offer] = field(default_factory=list)
    best: Offer | None = None
    unit: str = "ltr"
    error: str | None = None

    def as_dict(self) -> dict[str, Any]:
        w = self.watch
        return {
            "id": w["id"],
            "name": w["name"],
            "slug": w["slug"],
            "price": w["price"],
            "notify": w["notify"],
            "unit": self.unit,
            "hit": bool(self.hits),
            "matches": len(self.hits),
            "best": self.best.as_dict() if self.best else None,
            "error": self.error,
            "created": w.get("created"),
        }


class WatchlistCoordinator(DataUpdateCoordinator[list[WatchState]]):
    """Henter siderne for alle overvågninger og sender besked ved nye tilbud."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN}_watchlist",
            update_interval=timedelta(hours=int(entry.options.get("update_hours", 12))),
        )
        self.mode = "watchlist"
        self._store: Store[dict[str, Any]] = Store(hass, 1, f"{DOMAIN}.watchlist")
        self.watches: list[dict[str, Any]] = []
        self.fetched: datetime | None = None

    async def async_load(self) -> None:
        stored = await self._store.async_load() or {}
        self.watches = stored.get("watches", [])

    async def _async_save(self) -> None:
        await self._store.async_save({"watches": self.watches})

    def find(self, slug: str) -> dict[str, Any] | None:
        return next((w for w in self.watches if w["slug"] == slug), None)

    async def async_add(
        self,
        *,
        name: str,
        slug: str,
        price: float,
        notify: list[str],
        query: str = "",
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Opret eller opdatér overvågningen af en vare."""
        watch = self.find(slug)
        if watch is None:
            watch = {
                "id": uuid.uuid4().hex[:8],
                "name": name,
                "slug": slug,
                "query": query,
                "filters": {**DEFAULTS, **NEW_DEFAULTS, **(filters or {})},
                "created": dt_util.utcnow().isoformat(),
            }
            self.watches.append(watch)
        watch.update(price=round(price, 2), notify=notify, sent=[])
        await self._async_save()
        await self.async_refresh()
        return watch

    async def async_update_watch(self, watch_id: str, price: float | None, notify: list[str] | None) -> dict[str, Any]:
        watch = self._get(watch_id)
        if price is not None:
            watch["price"] = round(price, 2)
            watch["sent"] = []
        if notify is not None:
            watch["notify"] = notify
        await self._async_save()
        await self.async_refresh()
        return watch

    async def async_remove(self, watch_id: str) -> None:
        self._get(watch_id)
        self.watches = [w for w in self.watches if w["id"] != watch_id]
        await self._async_save()
        await self.async_refresh()

    def _get(self, watch_id: str) -> dict[str, Any]:
        for watch in self.watches:
            if watch["id"] == watch_id:
                return watch
        raise KeyError(watch_id)

    async def _async_update_data(self) -> list[WatchState]:
        session = async_get_clientsession(self.hass)
        today = dt_util.now().date().isoformat()
        pages: dict[str, Any] = {}
        states: list[WatchState] = []
        changed = False

        for watch in list(self.watches):
            state = WatchState(watch=watch)
            slug = watch["slug"]
            if slug not in pages:
                try:
                    pages[slug] = await async_fetch_offers(session, slug)
                except TilbudsugenError as err:
                    pages[slug] = err
            page = pages[slug]
            if isinstance(page, Exception):
                state.error = str(page)
                states.append(state)
                continue

            opts = {**DEFAULTS, **NEW_DEFAULTS, **watch.get("filters", {})}
            query = words(watch.get("query", ""), sep="")
            selection = select_offers(page.offers, opts, today, query, opts.get("category", AUTO))
            state.unit = selection.unit
            state.best = selection.matched[0] if selection.matched else None
            state.hits = [o for o in selection.matched if o.unit_price <= watch["price"]]

            sent = set(watch.get("sent", []))
            new = [o for o in state.hits if o.id not in sent]
            if new:
                await self._async_notify(watch, new, state.unit)
            current = sorted(o.id for o in state.hits)
            if current != watch.get("sent", []):
                watch["sent"] = current
                changed = True
            states.append(state)

        if changed:
            await self._async_save()
        self.fetched = dt_util.utcnow()
        return states

    async def _async_notify(self, watch: dict[str, Any], offers: list[Offer], unit: str) -> None:
        lines = [describe(o) for o in offers[:3]]
        if len(offers) > 3:
            lines.append(f"+ {len(offers) - 3} tilbud mere")
        data = {
            "title": f"{watch['name']} under {kr(watch['price'])} kr/{_UNITS.get(unit, 'stk')}",
            "message": "\n".join(lines),
            "data": {"url": offers[0].url, "clickAction": offers[0].url, "tag": f"{DOMAIN}_{watch['id']}"},
        }
        for target in watch.get("notify", []):
            try:
                await self.hass.services.async_call("notify", target, data, blocking=True)
            except Exception:  # noqa: BLE001 – en enhed må ikke stoppe de andre
                _LOGGER.exception("Kunne ikke sende besked til notify.%s", target)


def slug_for(text: str) -> str:
    return normalize_search(text)
