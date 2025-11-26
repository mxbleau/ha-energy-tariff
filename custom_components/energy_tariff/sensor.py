"""Sensor platform for Energy Tariff."""
from __future__ import annotations
from datetime import datetime, time
import logging
import holidays

from homeassistant.components.sensor import SensorEntity, SensorStateClass, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import (
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

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize the Energy Tariff sensor."""
    # Combine original data with any new options updates
    config = {**config_entry.data, **config_entry.options}
    name = config.get("name", "Energy Tariff")
    
    entity = EnergyTariffSensor(name, config)
    async_add_entities([entity], True)


class EnergyTariffSensor(SensorEntity):
    """Representation of an Energy Tariff sensor."""

    _attr_icon = "mdi:cash"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "USD/kWh" # Or your local currency symbol

    def __init__(self, name: str, config: dict):
        """Initialize the sensor."""
        self._attr_name = name
        self._attr_unique_id = f"energy_tariff_{name.lower().replace(' ', '_')}"
        self._config = config
        self._us_holidays = holidays.US()

    def update(self) -> None:
        """Fetch new state data for the sensor."""
        now = dt_util.now()
        
        if self._config[CONF_STRATEGY] == STRATEGY_FIXED:
            self._attr_native_value = self._config[CONF_PRICE_FIXED]
            self._attr_extra_state_attributes = {"period": "fixed"}
            return

        # Time of Use Logic
        is_weekend = now.weekday() >= 5
        is_holiday = now.date() in self._us_holidays
        
        # Check overrides for Weekend/Holiday
        if self._config.get(CONF_WEEKENDS_OFFPEAK) and is_weekend:
            period = "off_peak"
            is_peak_time = False
        elif self._config.get(CONF_HOLIDAYS_OFFPEAK) and is_holiday:
            period = "off_peak"
            is_peak_time = False
        else:
            # Check Time Window
            try:
                current_time = now.time()
                start_str = self._config[CONF_PEAK_START]
                end_str = self._config[CONF_PEAK_END]
                
                start_time = datetime.strptime(start_str, "%H:%M").time()
                end_time = datetime.strptime(end_str, "%H:%M").time()
                
                # Check for Midnight Crossing
                if start_time < end_time:
                    # Normal day (e.g., 15:00 to 19:00)
                    is_peak_time = start_time <= current_time < end_time
                else:
                    # Midnight crossing (e.g., 22:00 to 06:00)
                    # Peak if time is after 22:00 OR before 06:00
                    is_peak_time = current_time >= start_time or current_time < end_time
                    
                period = "peak" if is_peak_time else "off_peak"
            
            except (ValueError, TypeError):
                # Fallback in case of bad data
                _LOGGER.error("Invalid time format in Energy Tariff config")
                is_peak_time = False
                period = "error"

        # Check Season
        is_summer = now.month in self._config[CONF_SUMMER_MONTHS]
        season = "summer" if is_summer else "winter"

        # Determine Price
        if is_summer:
            price = (
                self._config[CONF_PRICE_SUMMER_PEAK]
                if is_peak_time
                else self._config[CONF_PRICE_SUMMER_OFFPEAK]
            )
        else:
            price = (
                self._config[CONF_PRICE_WINTER_PEAK]
                if is_peak_time
                else self._config[CONF_PRICE_WINTER_OFFPEAK]
            )

        self._attr_native_value = price
        self._attr_extra_state_attributes = {
            "period": period,
            "season": season,
            "is_holiday": is_holiday,
            "is_weekend": is_weekend
        }