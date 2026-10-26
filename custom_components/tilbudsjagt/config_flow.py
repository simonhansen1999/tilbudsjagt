"""Config flow for Tilbudsjagt."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
)

from .api import TilbudsugenError, async_fetch_offers, normalize_search
from .const import (
    ALL,
    AUTO,
    CONF_CATEGORY,
    CONF_EXCLUDE_CHAINS,
    CONF_INCLUDE_BORDER,
    CONF_INCLUDE_CHAINS,
    CONF_INCLUDE_DEPOSIT,
    CONF_MAX_RESULTS,
    CONF_MIN_UNITS,
    CONF_MODE,
    CONF_NAME,
    CONF_NAME_CONTAINS,
    CONF_NAME_EXCLUDES,
    CONF_ONE_PER_CHAIN,
    CONF_PACKAGE,
    CONF_SEARCH,
    CONF_SLUG,
    CONF_UNIT,
    CONF_UPDATE_HOURS,
    DEFAULTS,
    DOMAIN,
    KNOWN_CHAINS,
    MODE_PRODUCT,
    MODE_SEARCH,
    NEW_DEFAULTS,
    PACKAGES,
    UNITS,
)


def _number(minimum: int, maximum: int) -> NumberSelector:
    return NumberSelector(NumberSelectorConfig(min=minimum, max=maximum, step=1, mode=NumberSelectorMode.BOX))


def _select(options: list[str], key: str | None = None, multiple: bool = False) -> SelectSelector:
    config = SelectSelectorConfig(
        options=options, multiple=multiple, custom_value=multiple, mode=SelectSelectorMode.DROPDOWN
    )
    if key:
        config["translation_key"] = key
    return SelectSelector(config)


def _filter_schema(
    mode: str, current: dict[str, Any], chains: list[str], categories: list[str]
) -> vol.Schema:
    opts = {**DEFAULTS, **current}
    chain_options = sorted(
        set(KNOWN_CHAINS) | set(chains) | set(opts[CONF_INCLUDE_CHAINS]) | set(opts[CONF_EXCLUDE_CHAINS])
    )
    fields: dict[Any, Any] = {}

    if mode == MODE_PRODUCT:
        category_options = [AUTO, ALL, *sorted(set(categories) - {AUTO, ALL})]
        if opts[CONF_CATEGORY] not in category_options:
            category_options.append(opts[CONF_CATEGORY])
        fields[vol.Optional(CONF_NAME_CONTAINS, default=opts[CONF_NAME_CONTAINS])] = TextSelector()
        fields[vol.Optional(CONF_NAME_EXCLUDES, default=opts[CONF_NAME_EXCLUDES])] = TextSelector()
        fields[vol.Required(CONF_CATEGORY, default=opts[CONF_CATEGORY])] = _select(category_options, "category")
    else:
        fields[vol.Optional(CONF_NAME_EXCLUDES, default=opts[CONF_NAME_EXCLUDES])] = TextSelector()

    fields.update(
        {
            vol.Required(CONF_UNIT, default=opts[CONF_UNIT]): _select(UNITS, "unit"),
            vol.Required(CONF_PACKAGE, default=opts[CONF_PACKAGE]): _select(PACKAGES, "package"),
            vol.Required(CONF_MIN_UNITS, default=opts[CONF_MIN_UNITS]): _number(1, 100),
            vol.Optional(CONF_INCLUDE_CHAINS, default=opts[CONF_INCLUDE_CHAINS]): _select(chain_options, multiple=True),
            vol.Optional(CONF_EXCLUDE_CHAINS, default=opts[CONF_EXCLUDE_CHAINS]): _select(chain_options, multiple=True),
            vol.Required(CONF_INCLUDE_BORDER, default=opts[CONF_INCLUDE_BORDER]): BooleanSelector(),
            vol.Required(CONF_INCLUDE_DEPOSIT, default=opts[CONF_INCLUDE_DEPOSIT]): BooleanSelector(),
            vol.Required(CONF_ONE_PER_CHAIN, default=opts[CONF_ONE_PER_CHAIN]): BooleanSelector(),
            vol.Required(CONF_UPDATE_HOURS, default=opts[CONF_UPDATE_HOURS]): _number(1, 24),
        }
    )
    if mode == MODE_PRODUCT:
        fields[vol.Required(CONF_MAX_RESULTS, default=opts[CONF_MAX_RESULTS])] = _number(1, 50)
    return vol.Schema(fields)


def _clean(user_input: dict[str, Any]) -> dict[str, Any]:
    """NumberSelector giver floats; gem hele tal."""
    for key in (CONF_MIN_UNITS, CONF_MAX_RESULTS, CONF_UPDATE_HOURS):
        if key in user_input:
            user_input[key] = int(user_input[key])
    return user_input


class TilbudsjagtConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._mode = MODE_PRODUCT
        self._slug = ""
        self._name = ""
        self._chains: list[str] = []
        self._categories: list[str] = []

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        return self.async_show_menu(step_id="user", menu_options=[MODE_PRODUCT, MODE_SEARCH])

    async def async_step_product(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            self._mode = MODE_PRODUCT
            self._slug = normalize_search(user_input[CONF_SEARCH])
            await self.async_set_unique_id(self._slug)
            self._abort_if_unique_id_configured()
            try:
                page = await async_fetch_offers(async_get_clientsession(self.hass), self._slug)
            except TilbudsugenError:
                errors["base"] = "cannot_connect"
            else:
                if not page.offers:
                    errors["base"] = "no_offers"
                else:
                    self._chains = page.chains
                    self._categories = sorted({o.category for o in page.offers if o.category})
                    self._name = user_input.get(CONF_NAME) or user_input[CONF_SEARCH].replace("-", " ").title()
                    return await self.async_step_filters()

        return self.async_show_form(
            step_id="product",
            data_schema=vol.Schema(
                {vol.Required(CONF_SEARCH): TextSelector(), vol.Optional(CONF_NAME): TextSelector()}
            ),
            errors=errors,
        )

    async def async_step_search(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            self._mode = MODE_SEARCH
            self._name = user_input[CONF_NAME].strip() or "Tilbudssøgning"
            await self.async_set_unique_id(f"search_{normalize_search(self._name)}")
            self._abort_if_unique_id_configured()
            return await self.async_step_filters()

        return self.async_show_form(
            step_id="search",
            data_schema=vol.Schema({vol.Required(CONF_NAME, default="Tilbudssøgning"): TextSelector()}),
        )

    async def async_step_filters(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            data = {CONF_MODE: self._mode}
            if self._mode == MODE_PRODUCT:
                data[CONF_SLUG] = self._slug
            options = _clean(user_input)
            if self._mode == MODE_SEARCH:
                options[CONF_CATEGORY] = AUTO
            return self.async_create_entry(title=self._name, data=data, options=options)

        return self.async_show_form(
            step_id="filters",
            data_schema=_filter_schema(self._mode, NEW_DEFAULTS, self._chains, self._categories),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry) -> TilbudsjagtOptionsFlow:
        return TilbudsjagtOptionsFlow()


class TilbudsjagtOptionsFlow(OptionsFlow):
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        mode = self.config_entry.data.get(CONF_MODE, MODE_PRODUCT)
        if user_input is not None:
            options = _clean(user_input)
            if mode == MODE_SEARCH:
                options[CONF_CATEGORY] = AUTO
            return self.async_create_entry(data=options)

        coordinator = getattr(self.config_entry, "runtime_data", None)
        data = coordinator.data if coordinator else None
        chains = data.chains if data else []
        categories = [name for name, _ in data.categories] if data else []
        return self.async_show_form(
            step_id="init",
            data_schema=_filter_schema(mode, dict(self.config_entry.options), chains, categories),
        )
