"""Søgefelt for en Tilbudsjagt-søgning."""

from __future__ import annotations

from homeassistant.components.text import TextEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .coordinator import TilbudsjagtConfigEntry, TilbudsjagtCoordinator
from .sensor import TilbudsjagtEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TilbudsjagtConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([QueryText(entry.runtime_data, entry)])


class QueryText(TilbudsjagtEntity, TextEntity, RestoreEntity):
    """Det der søges efter. Ændres det, hentes nye tilbud."""

    _attr_translation_key = "query"
    _attr_icon = "mdi:magnify"
    _attr_native_max = 60

    def __init__(self, coordinator: TilbudsjagtCoordinator, entry: TilbudsjagtConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_query"

    @property
    def native_value(self) -> str:
        return self.coordinator.query

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.coordinator.query_entity_id = self.entity_id
        last = await self.async_get_last_state()
        if last and last.state not in ("unknown", "unavailable", ""):
            await self.coordinator.async_set_query(last.state)
        else:
            self.coordinator.async_update_listeners()

    async def async_set_value(self, value: str) -> None:
        await self.coordinator.async_set_query(value)
