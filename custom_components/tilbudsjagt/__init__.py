"""Tilbudsjagt – billigste tilbud fra tilbudsugen.dk."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .card import async_register_card
from .const import CONF_MODE, DOMAIN, MODE_SEARCH
from .coordinator import TilbudsjagtConfigEntry, TilbudsjagtCoordinator

PRODUCT_PLATFORMS = [Platform.SENSOR]
SEARCH_PLATFORMS = [Platform.SENSOR, Platform.SELECT, Platform.TEXT]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


def _platforms(entry: TilbudsjagtConfigEntry) -> list[Platform]:
    return SEARCH_PLATFORMS if entry.data.get(CONF_MODE) == MODE_SEARCH else PRODUCT_PLATFORMS


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Registrér det medfølgende dashboard-kort."""
    await async_register_card(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: TilbudsjagtConfigEntry) -> bool:
    coordinator = TilbudsjagtCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    await hass.config_entries.async_forward_entry_setups(entry, _platforms(entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: TilbudsjagtConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, _platforms(entry))


async def _async_reload(hass: HomeAssistant, entry: TilbudsjagtConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
