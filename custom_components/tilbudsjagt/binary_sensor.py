"""Prisalarm: tændt når mindst én overvågning har fundet et tilbud under prisen."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import TilbudsjagtConfigEntry
from .sensor import WatchlistEntity
from .watchlist import WatchlistCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TilbudsjagtConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([PriceAlarm(entry.runtime_data, entry)])


class PriceAlarm(WatchlistEntity, BinarySensorEntity):
    _attr_translation_key = "price_alarm"

    def __init__(self, coordinator: WatchlistCoordinator, entry: TilbudsjagtConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_price_alarm"

    @property
    def is_on(self) -> bool:
        return any(s.hits for s in self.coordinator.data or [])

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"watches": [s.watch["name"] for s in self.coordinator.data or [] if s.hits]}
