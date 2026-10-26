"""Kategorivalg for en Tilbudsjagt-søgning."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import ALL, AUTO
from .coordinator import TilbudsjagtConfigEntry, TilbudsjagtCoordinator
from .sensor import TilbudsjagtEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TilbudsjagtConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([CategorySelect(entry.runtime_data, entry)])


class CategorySelect(TilbudsjagtEntity, SelectEntity):
    """Varekategori. 'auto' vælger den kategori de fleste træffere hører til."""

    _attr_translation_key = "category"
    _attr_icon = "mdi:shape"

    def __init__(self, coordinator: TilbudsjagtCoordinator, entry: TilbudsjagtConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_category"

    @property
    def options(self) -> list[str]:
        found = [name for name, _ in self.coordinator.data.categories]
        choice = self.coordinator.category_choice
        extra = [choice] if choice not in (AUTO, ALL, *found) else []
        return [AUTO, ALL, *found, *extra]

    @property
    def current_option(self) -> str:
        return self.coordinator.category_choice

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.coordinator.category_entity_id = self.entity_id
        self.coordinator.async_update_listeners()

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_set_category(option)
