"""Sensor med billigste tilbud."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, BASE_URL, DOMAIN
from .coordinator import TilbudsjagtConfigEntry, TilbudsjagtCoordinator

UNIT_SHORT = {"ltr.": "l", "kg.": "kg", "stk.": "stk"}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TilbudsjagtConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([TilbudsjagtSensor(entry.runtime_data, entry)])


class TilbudsjagtSensor(CoordinatorEntity[TilbudsjagtCoordinator], SensorEntity):
    """Billigste enhedspris. Alle viste tilbud ligger i attributten 'offers'."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_attribution = ATTRIBUTION
    _attr_icon = "mdi:tag-heart"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2
    _unrecorded_attributes = frozenset({"offers", "chains"})

    def __init__(self, coordinator: TilbudsjagtCoordinator, entry: TilbudsjagtConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = entry.entry_id
        unit = coordinator.options["unit"]
        self._attr_native_unit_of_measurement = (
            f"kr/{UNIT_SHORT[unit]}" if unit in UNIT_SHORT else "kr"
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Tilbudsugen.dk",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url=f"{BASE_URL}/offer/{coordinator.slug}",
        )

    @property
    def native_value(self) -> float | None:
        offers = self.coordinator.data.offers
        return offers[0].unit_price if offers else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data
        return {
            "offers": [o.as_dict() for o in data.offers],
            "chains": data.chains,
            "total_offers": data.total,
            "unit": self.coordinator.options["unit"],
            "url": f"{BASE_URL}/offer/{self.coordinator.slug}",
            "last_fetch": data.fetched.isoformat(),
        }
