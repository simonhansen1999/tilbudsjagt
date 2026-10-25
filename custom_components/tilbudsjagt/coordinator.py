"""Coordinator for Tilbudsjagt."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import Offer, TilbudsugenError, async_fetch_offers, filter_offers
from .const import CONF_SLUG, CONF_UPDATE_HOURS, DEFAULTS, DOMAIN

_LOGGER = logging.getLogger(__name__)

type TilbudsjagtConfigEntry = ConfigEntry[TilbudsjagtCoordinator]


@dataclass
class TilbudsjagtData:
    offers: list[Offer]
    chains: list[str]
    total: int
    fetched: datetime


class TilbudsjagtCoordinator(DataUpdateCoordinator[TilbudsjagtData]):
    """Henter siden og filtrerer efter brugerens valg."""

    def __init__(self, hass: HomeAssistant, entry: TilbudsjagtConfigEntry) -> None:
        self.options = {**DEFAULTS, **entry.options}
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN}_{entry.data[CONF_SLUG]}",
            update_interval=timedelta(hours=self.options[CONF_UPDATE_HOURS]),
        )
        self.slug: str = entry.data[CONF_SLUG]

    async def _async_update_data(self) -> TilbudsjagtData:
        try:
            offers = await async_fetch_offers(async_get_clientsession(self.hass), self.slug)
        except TilbudsugenError as err:
            raise UpdateFailed(str(err)) from err

        today = dt_util.now().date().isoformat()
        return TilbudsjagtData(
            offers=filter_offers(offers, self.options, today),
            chains=sorted({o.chain for o in offers if o.chain}),
            total=len(offers),
            fetched=dt_util.utcnow(),
        )
