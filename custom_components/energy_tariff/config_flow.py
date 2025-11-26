"""Config flow for Energy Tariff integration."""
from __future__ import annotations

import logging
from typing import Any
from datetime import datetime

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
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
    ERROR_INVALID_TIME_FORMAT,
    ERROR_SAME_START_END,
    ERROR_NEGATIVE_PRICE,
)

_LOGGER = logging.getLogger(__name__)

def validate_tou_input(user_input: dict[str, Any]) -> dict[str, str]:
    """Validate Time of Use input data."""
    errors = {}

    # 1. Validate Time Formats
    try:
        start_time = datetime.strptime(user_input[CONF_PEAK_START], "%H:%M").time()
        end_time = datetime.strptime(user_input[CONF_PEAK_END], "%H:%M").time()
        
        # 2. Validate Logic (Start != End)
        # Note: We allow Start > End to support midnight crossing (e.g. 22:00 to 06:00)
        if start_time == end_time:
            errors["base"] = ERROR_SAME_START_END

    except ValueError:
        errors["base"] = ERROR_INVALID_TIME_FORMAT

    # 3. Validate Prices (Must be non-negative)
    price_keys = [
        CONF_PRICE_SUMMER_PEAK, CONF_PRICE_SUMMER_OFFPEAK,
        CONF_PRICE_WINTER_PEAK, CONF_PRICE_WINTER_OFFPEAK
    ]
    for key in price_keys:
        if user_input.get(key, 0) < 0:
            errors["base"] = ERROR_NEGATIVE_PRICE
            break
            
    return errors

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

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

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
        errors = {}
        if user_input is not None:
            if user_input[CONF_PRICE_FIXED] < 0:
                errors["base"] = ERROR_NEGATIVE_PRICE
            else:
                final_data = {**self._data, **user_input}
                return self.async_create_entry(title=self._data["name"], data=final_data)

        return self.async_show_form(
            step_id="fixed",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PRICE_FIXED, default=0.15): float,
                }
            ),
            errors=errors
        )

    async def async_step_tou(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the Time of Use configuration step."""
        errors = {}
        if user_input is not None:
            errors = validate_tou_input(user_input)
            if not errors:
                final_data = {**self._data, **user_input}
                return self.async_create_entry(title=self._data["name"], data=final_data)

        # Defaults or previous input
        defaults = user_input or {
            CONF_PEAK_START: "15:00",
            CONF_PEAK_END: "19:00",
            CONF_PRICE_SUMMER_PEAK: 0.2339,
            CONF_PRICE_SUMMER_OFFPEAK: 0.1764,
            CONF_PRICE_WINTER_PEAK: 0.1912,
            CONF_PRICE_WINTER_OFFPEAK: 0.1764,
            CONF_SUMMER_MONTHS: [6, 7, 8, 9],
            CONF_WEEKENDS_OFFPEAK: True,
            CONF_HOLIDAYS_OFFPEAK: True,
        }

        return self.async_show_form(
            step_id="tou",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PEAK_START, default=defaults.get(CONF_PEAK_START)): str,
                    vol.Required(CONF_PEAK_END, default=defaults.get(CONF_PEAK_END)): str,
                    
                    vol.Required(CONF_PRICE_SUMMER_PEAK, default=defaults.get(CONF_PRICE_SUMMER_PEAK)): float,
                    vol.Required(CONF_PRICE_SUMMER_OFFPEAK, default=defaults.get(CONF_PRICE_SUMMER_OFFPEAK)): float,
                    vol.Required(CONF_PRICE_WINTER_PEAK, default=defaults.get(CONF_PRICE_WINTER_PEAK)): float,
                    vol.Required(CONF_PRICE_WINTER_OFFPEAK, default=defaults.get(CONF_PRICE_WINTER_OFFPEAK)): float,

                    vol.Required(CONF_SUMMER_MONTHS, default=defaults.get(CONF_SUMMER_MONTHS)): cv.multi_select(
                        {
                            1: "January", 2: "February", 3: "March", 4: "April",
                            5: "May", 6: "June", 7: "July", 8: "August",
                            9: "September", 10: "October", 11: "November", 12: "December"
                        }
                    ),
                    
                    vol.Required(CONF_WEEKENDS_OFFPEAK, default=defaults.get(CONF_WEEKENDS_OFFPEAK)): bool,
                    vol.Required(CONF_HOLIDAYS_OFFPEAK, default=defaults.get(CONF_HOLIDAYS_OFFPEAK)): bool,
                }
            ),
            errors=errors
        )


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Energy Tariff."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors = {}
        
        # Merge data and options to get current settings
        current_config = {**self.config_entry.data, **self.config_entry.options}
        strategy = current_config.get(CONF_STRATEGY, STRATEGY_TOU)

        if user_input is not None:
            if strategy == STRATEGY_FIXED:
                if user_input[CONF_PRICE_FIXED] < 0:
                    errors["base"] = ERROR_NEGATIVE_PRICE
            else:
                errors = validate_tou_input(user_input)
            
            if not errors:
                return self.async_create_entry(title="", data=user_input)

        if strategy == STRATEGY_FIXED:
            schema = vol.Schema({
                vol.Required(
                    CONF_PRICE_FIXED, 
                    default=user_input.get(CONF_PRICE_FIXED, current_config.get(CONF_PRICE_FIXED, 0.15)) if user_input else current_config.get(CONF_PRICE_FIXED, 0.15)
                ): float,
            })
        else:
            # Time of Use Schema
            month_options = {
                1: "January", 2: "February", 3: "March", 4: "April",
                5: "May", 6: "June", 7: "July", 8: "August",
                9: "September", 10: "October", 11: "November", 12: "December"
            }
            
            # Use user_input if available (to preserve what they typed if there was an error), otherwise current config
            defaults = user_input if user_input else current_config

            schema = vol.Schema({
                vol.Required(CONF_PEAK_START, default=defaults.get(CONF_PEAK_START, "15:00")): str,
                vol.Required(CONF_PEAK_END, default=defaults.get(CONF_PEAK_END, "19:00")): str,
                
                vol.Required(CONF_PRICE_SUMMER_PEAK, default=defaults.get(CONF_PRICE_SUMMER_PEAK, 0.2339)): float,
                vol.Required(CONF_PRICE_SUMMER_OFFPEAK, default=defaults.get(CONF_PRICE_SUMMER_OFFPEAK, 0.1764)): float,
                vol.Required(CONF_PRICE_WINTER_PEAK, default=defaults.get(CONF_PRICE_WINTER_PEAK, 0.1912)): float,
                vol.Required(CONF_PRICE_WINTER_OFFPEAK, default=defaults.get(CONF_PRICE_WINTER_OFFPEAK, 0.1764)): float,

                vol.Required(CONF_SUMMER_MONTHS, default=defaults.get(CONF_SUMMER_MONTHS, [6, 7, 8, 9])): cv.multi_select(month_options),
                
                vol.Required(CONF_WEEKENDS_OFFPEAK, default=defaults.get(CONF_WEEKENDS_OFFPEAK, True)): bool,
                vol.Required(CONF_HOLIDAYS_OFFPEAK, default=defaults.get(CONF_HOLIDAYS_OFFPEAK, True)): bool,
            })

        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)