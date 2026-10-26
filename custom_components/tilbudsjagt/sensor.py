"""Sensorer for Tilbudsjagt."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, BASE_URL, DOMAIN
from .coordinator import TilbudsjagtConfigEntry, TilbudsjagtCoordinator

UNIT_SHORT = {"ltr": "l", "kg": "kg", "stk": "stk"}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TilbudsjagtConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        [TilbudsjagtSensor(coordinator, entry), CheapestStoreSensor(coordinator, entry)]
    )


def unit_text(unit: str) -> str:
    return f"kr/{UNIT_SHORT[unit]}" if unit in UNIT_SHORT else "kr"


class TilbudsjagtEntity(CoordinatorEntity[TilbudsjagtCoordinator]):
    """Fælles enhed for alle entiteter på en vare eller søgning."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: TilbudsjagtCoordinator, entry: TilbudsjagtConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Tilbudsugen.dk",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url=f"{BASE_URL}/offer/{coordinator.slug}" if coordinator.slug else BASE_URL,
        )


class TilbudsjagtSensor(TilbudsjagtEntity, SensorEntity):
    """Billigste enhedspris. Alle viste tilbud ligger i attributten 'offers'."""

    _attr_name = None
    _attr_suggested_display_precision = 2
    _unrecorded_attributes = frozenset({"offers", "chains", "categories"})

    def __init__(self, coordinator: TilbudsjagtCoordinator, entry: TilbudsjagtConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = entry.entry_id
        self._attr_icon = "mdi:magnify" if coordinator.is_search else "mdi:tag-heart"
        # Kun en fast enhed giver mening i statistik
        if coordinator.options["unit"] in UNIT_SHORT:
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self) -> str:
        return unit_text(self.coordinator.data.unit)

    @property
    def native_value(self) -> float | None:
        offers = self.coordinator.data.offers
        return offers[0].unit_price if offers else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        coordinator = self.coordinator
        data = coordinator.data
        attrs: dict[str, Any] = {
            "offers": [o.as_dict() for o in data.offers],
            "chains": data.chains,
            "categories": [{"name": n, "count": c} for n, c in data.categories],
            "category": data.category,
            "total_offers": data.total,
            "unit": data.unit,
            "include_deposit": coordinator.options["include_deposit"],
            "one_per_chain": coordinator.options["one_per_chain"],
            "mode": coordinator.mode,
            "url": f"{BASE_URL}/offer/{coordinator.slug}" if coordinator.slug else BASE_URL,
            "last_fetch": data.fetched.isoformat() if data.fetched else None,
        }
        if coordinator.is_search:
            attrs.update(
                query=data.query,
                category_choice=coordinator.category_choice,
                query_entity=coordinator.query_entity_id,
                category_entity=coordinator.category_entity_id,
            )
        return attrs


class CheapestStoreSensor(TilbudsjagtEntity, SensorEntity):
    """Kæden med den laveste enhedspris. Alle kæders priser ligger i 'prices'."""

    _attr_translation_key = "cheapest_store"
    _attr_icon = "mdi:store-marker"
    _unrecorded_attributes = frozenset({"prices"})

    def __init__(self, coordinator: TilbudsjagtCoordinator, entry: TilbudsjagtConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_cheapest_store"

    @property
    def native_value(self) -> str | None:
        per_chain = self.coordinator.data.per_chain
        return per_chain[0].chain if per_chain else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        per_chain = self.coordinator.data.per_chain
        best = per_chain[0] if per_chain else None
        return {
            "unit_price": best.unit_price if best else None,
            "price": best.price if best else None,
            "product": best.name if best else None,
            "url": best.url if best else None,
            "price_unit": unit_text(self.coordinator.data.unit),
            "prices": {o.chain: o.unit_price for o in per_chain},
        }
