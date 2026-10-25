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
    CONF_EXCLUDE_CHAINS,
    CONF_INCLUDE_BORDER,
    CONF_INCLUDE_DEPOSIT,
    CONF_MAX_RESULTS,
    CONF_MIN_UNITS,
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
    PACKAGES,
    UNITS,
)


def _number(minimum: int, maximum: int) -> NumberSelector:
    return NumberSelector(
        NumberSelectorConfig(min=minimum, max=maximum, step=1, mode=NumberSelectorMode.BOX)
    )


def _filter_schema(chains: list[str], current: dict[str, Any]) -> vol.Schema:
    opts = {**DEFAULTS, **current}
    chain_options = sorted(set(chains) | set(opts[CONF_EXCLUDE_CHAINS]))
    return vol.Schema(
        {
            vol.Optional(CONF_NAME_CONTAINS, default=opts[CONF_NAME_CONTAINS]): TextSelector(),
            vol.Optional(CONF_NAME_EXCLUDES, default=opts[CONF_NAME_EXCLUDES]): TextSelector(),
            vol.Required(CONF_UNIT, default=opts[CONF_UNIT]): SelectSelector(
                SelectSelectorConfig(
                    options=UNITS, mode=SelectSelectorMode.DROPDOWN, translation_key="unit"
                )
            ),
            vol.Required(CONF_PACKAGE, default=opts[CONF_PACKAGE]): SelectSelector(
                SelectSelectorConfig(
                    options=PACKAGES, mode=SelectSelectorMode.DROPDOWN, translation_key="package"
                )
            ),
            vol.Required(CONF_MIN_UNITS, default=opts[CONF_MIN_UNITS]): _number(1, 100),
            vol.Optional(CONF_EXCLUDE_CHAINS, default=opts[CONF_EXCLUDE_CHAINS]): SelectSelector(
                SelectSelectorConfig(
                    options=chain_options,
                    multiple=True,
                    custom_value=True,
                    mode=SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(CONF_INCLUDE_BORDER, default=opts[CONF_INCLUDE_BORDER]): BooleanSelector(),
            vol.Required(CONF_INCLUDE_DEPOSIT, default=opts[CONF_INCLUDE_DEPOSIT]): BooleanSelector(),
            vol.Required(CONF_ONE_PER_CHAIN, default=opts[CONF_ONE_PER_CHAIN]): BooleanSelector(),
            vol.Required(CONF_MAX_RESULTS, default=opts[CONF_MAX_RESULTS]): _number(1, 20),
            vol.Required(CONF_UPDATE_HOURS, default=opts[CONF_UPDATE_HOURS]): _number(1, 24),
        }
    )


def _clean(user_input: dict[str, Any]) -> dict[str, Any]:
    """NumberSelector giver floats; gem hele tal."""
    for key in (CONF_MIN_UNITS, CONF_MAX_RESULTS, CONF_UPDATE_HOURS):
        user_input[key] = int(user_input[key])
    return user_input


class TilbudsjagtConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._slug = ""
        self._name = ""
        self._chains: list[str] = []

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            self._slug = normalize_search(user_input[CONF_SEARCH])
            await self.async_set_unique_id(self._slug)
            self._abort_if_unique_id_configured()
            try:
                offers = await async_fetch_offers(async_get_clientsession(self.hass), self._slug)
            except TilbudsugenError:
                errors["base"] = "cannot_connect"
            else:
                if not offers:
                    errors["base"] = "no_offers"
                else:
                    self._chains = sorted({o.chain for o in offers if o.chain})
                    self._name = (
                        user_input.get(CONF_NAME)
                        or user_input[CONF_SEARCH].replace("-", " ").title()
                    )
                    return await self.async_step_filters()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SEARCH): TextSelector(),
                    vol.Optional(CONF_NAME): TextSelector(),
                }
            ),
            errors=errors,
        )

    async def async_step_filters(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(
                title=self._name, data={CONF_SLUG: self._slug}, options=_clean(user_input)
            )
        return self.async_show_form(
            step_id="filters",
            data_schema=_filter_schema(self._chains, {}),
            description_placeholders={"chains": str(len(self._chains))},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry) -> TilbudsjagtOptionsFlow:
        return TilbudsjagtOptionsFlow()


class TilbudsjagtOptionsFlow(OptionsFlow):
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=_clean(user_input))

        coordinator = getattr(self.config_entry, "runtime_data", None)
        chains = coordinator.data.chains if coordinator and coordinator.data else []
        return self.async_show_form(
            step_id="init", data_schema=_filter_schema(chains, dict(self.config_entry.options))
        )
