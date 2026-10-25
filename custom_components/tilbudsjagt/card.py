"""Registrerer det medfølgende dashboard-kort."""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration

from .const import DOMAIN

try:
    from homeassistant.components.lovelace.const import LOVELACE_DATA
except ImportError:  # ældre Home Assistant
    LOVELACE_DATA = "lovelace"

_LOGGER = logging.getLogger(__name__)

CARD_PATH = f"/{DOMAIN}/tilbudsjagt-card.js"
CARD_FILE = Path(__file__).parent / "frontend" / "tilbudsjagt-card.js"


async def async_register_card(hass: HomeAssistant) -> None:
    """Server kortet og tilføj det som dashboard-ressource."""
    await hass.http.async_register_static_paths(
        [StaticPathConfig(CARD_PATH, str(CARD_FILE), False)]
    )
    integration = await async_get_integration(hass, DOMAIN)
    url = f"{CARD_PATH}?v={integration.version}"

    if not await _async_set_resource(hass, url):
        # YAML-tilstand for ressourcer: læg kortet på alle sider i stedet
        add_extra_js_url(hass, url)


async def _async_set_resource(hass: HomeAssistant, url: str) -> bool:
    """Opret eller opdatér ressourcen. False hvis ressourcer ikke kan redigeres."""
    lovelace = hass.data.get(LOVELACE_DATA)
    resources = getattr(lovelace, "resources", None)
    if resources is None or not hasattr(resources, "async_create_item"):
        return False

    if not resources.loaded:
        await resources.async_load()
        resources.loaded = True

    for item in resources.async_items():
        if item["url"].split("?")[0] == CARD_PATH:
            if item["url"] != url:
                await resources.async_update_item(item["id"], {"res_type": "module", "url": url})
                _LOGGER.debug("Opdaterede kort-ressource til %s", url)
            return True

    await resources.async_create_item({"res_type": "module", "url": url})
    _LOGGER.debug("Oprettede kort-ressource %s", url)
    return True
