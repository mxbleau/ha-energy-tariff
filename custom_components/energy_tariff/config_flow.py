"""Config flow for Energy Tariff integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_STRATEGY,
    STRATEGY_FIXED,
    STRATEGY_TOU,
    CONF_PRICE_FIXED,
    CONF_PEAK_START,
    CONF_PEAK_END,
    CONF_SUMMER_MONTHS,
    CONF_PRICE_SUMMER_PEAK,
    CONF_PRICE_SUMMER_OFFPEAK,
    CONF_PRICE_WINTER_PEAK,
    CONF_PRICE_WINTER_OFFPEAK,
    CONF_WEEKENDS_OFFPEAK,
    CONF_HOLIDAYS_OFFPEAK,
)

_LOGGER = logging.getLogger(__name__)

# Schema for the initial step (choosing strategy)
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("name", default="My Energy Rate"): str,
        vol.Required(CONF_STRATEGY, default=STRATEGY_TOU): vol.In(
            {
                STRATEGY_FIXED: "Fixed Rate",
                STRATEGY_TOU: "Time of Use (Peak/Off-Peak)",
            }
        ),
    }
)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Energy Tariff."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        self._data = user_input

        if user_input[CONF_STRATEGY] == STRATEGY_FIXED:
            return await self.async_step_fixed()
        else:
            return await self.async_step_tou()

    async def async_step_fixed(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the fixed rate step."""
        if user_input is None:
            return self.async_show_form(
                step_id="fixed",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_PRICE_FIXED, default=0.15): float,
                    }
                ),
            )
        
        # Combine data and create entry
        final_data = {**self._data, **user_input}
        return self.async_create_entry(title=self._data["name"], data=final_data)

    async def async_step_tou(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the Time of Use configuration step."""
        if user_input is None:
            # Default to DTE 3-7 PM logic
            return self.async_show_form(
                step_id="tou",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_PEAK_START, default="15:00"): str,
                        vol.Required(CONF_PEAK_END, default="19:00"): str,
                        
                        vol.Required(CONF_PRICE_SUMMER_PEAK, default=0.2339): float,
                        vol.Required(CONF_PRICE_SUMMER_OFFPEAK, default=0.1764): float,
                        vol.Required(CONF_PRICE_WINTER_PEAK, default=0.1912): float,
                        vol.Required(CONF_PRICE_WINTER_OFFPEAK, default=0.1764): float,

                        vol.Required(CONF_SUMMER_MONTHS, default=[6, 7, 8, 9]): cv.multi_select(
                            {
                                1: "January", 2: "February", 3: "March", 4: "April",
                                5: "May", 6: "June", 7: "July", 8: "August",
                                9: "September", 10: "October", 11: "November", 12: "December"
                            }
                        ),
                        
                        vol.Required(CONF_WEEKENDS_OFFPEAK, default=True): bool,
                        vol.Required(CONF_HOLIDAYS_OFFPEAK, default=True): bool,
                    }
                ),
            )

        # Basic validation could go here (e.g. check time format), skipping for brevity
        final_data = {**self._data, **user_input}
        return self.async_create_entry(title=self._data["name"], data=final_data)