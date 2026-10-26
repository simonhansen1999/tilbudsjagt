"""Coordinator for Tilbudsjagt."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import (
    Offer,
    OfferPage,
    TilbudsugenError,
    async_fetch_offers,
    cheapest_per_chain,
    normalize_search,
    select_offers,
    top_offers,
    words,
)
from .const import (
    AUTO,
    CONF_MODE,
    CONF_SLUG,
    CONF_UPDATE_HOURS,
    DEFAULTS,
    DOMAIN,
    MODE_PRODUCT,
    MODE_SEARCH,
)

_LOGGER = logging.getLogger(__name__)

type TilbudsjagtConfigEntry = ConfigEntry[TilbudsjagtCoordinator]


@dataclass
class TilbudsjagtData:
    offers: list[Offer] = field(default_factory=list)
    per_chain: list[Offer] = field(default_factory=list)
    chains: list[str] = field(default_factory=list)
    categories: list[tuple[str, int]] = field(default_factory=list)
    category: str | None = None
    unit: str = "ltr"
    total: int = 0
    query: str = ""
    fetched: datetime | None = None


class TilbudsjagtCoordinator(DataUpdateCoordinator[TilbudsjagtData]):
    """Henter siden og filtrerer efter brugerens valg."""

    def __init__(self, hass: HomeAssistant, entry: TilbudsjagtConfigEntry) -> None:
        self.options = {**DEFAULTS, **entry.options}
        self.mode: str = entry.data.get(CONF_MODE, MODE_PRODUCT)
        self.slug: str = entry.data.get(CONF_SLUG, "")
        self.query = ""
        self.category_choice = AUTO
        self.query_entity_id: str | None = None
        self.category_entity_id: str | None = None
        self._page: OfferPage | None = None
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(hours=self.options[CONF_UPDATE_HOURS]),
        )

    @property
    def is_search(self) -> bool:
        return self.mode == MODE_SEARCH

    async def async_set_query(self, query: str) -> None:
        """Ny søgning: hent siden og nulstil kategori."""
        query = query.strip()
        if query != self.query:
            self.query = query
            self.category_choice = AUTO
            self._page = None
        await self.async_refresh()

    async def async_set_category(self, choice: str) -> None:
        """Skift kategori uden at hente siden igen."""
        self.category_choice = choice
        if self._page is not None and self.data is not None:
            self.async_set_updated_data(self._build(self._page, self.data.fetched))
        else:
            await self.async_refresh()

    async def _async_update_data(self) -> TilbudsjagtData:
        slug = normalize_search(self.query) if self.is_search else self.slug
        if not slug:
            self._page = None
            return TilbudsjagtData(unit=self.options["unit"], fetched=dt_util.utcnow())
        try:
            page = await async_fetch_offers(async_get_clientsession(self.hass), slug)
        except TilbudsugenError as err:
            raise UpdateFailed(str(err)) from err
        self._page = page
        return self._build(page, dt_util.utcnow())

    def _build(self, page: OfferPage, fetched: datetime | None) -> TilbudsjagtData:
        today = dt_util.now().date().isoformat()
        if self.is_search:
            selection = select_offers(
                page.offers, self.options, today, words(self.query, sep=""), self.category_choice
            )
        else:
            selection = select_offers(page.offers, self.options, today)
        return TilbudsjagtData(
            offers=top_offers(selection.matched, self.options),
            per_chain=cheapest_per_chain(selection.matched),
            chains=page.chains,
            categories=selection.categories,
            category=selection.category,
            unit=selection.unit,
            total=page.total,
            query=self.query,
            fetched=fetched,
        )
