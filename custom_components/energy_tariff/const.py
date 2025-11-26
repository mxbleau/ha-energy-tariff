"""Constants for the Energy Tariff integration."""

DOMAIN = "energy_tariff"

# Configuration Keys
CONF_STRATEGY = "strategy"
CONF_PRICE_FIXED = "price_fixed"

CONF_PEAK_START = "peak_start"
CONF_PEAK_END = "peak_end"
CONF_SUMMER_MONTHS = "summer_months"

CONF_PRICE_SUMMER_PEAK = "price_summer_peak"
CONF_PRICE_SUMMER_OFFPEAK = "price_summer_offpeak"
CONF_PRICE_WINTER_PEAK = "price_winter_peak"
CONF_PRICE_WINTER_OFFPEAK = "price_winter_offpeak"

CONF_WEEKENDS_OFFPEAK = "weekends_offpeak"
CONF_HOLIDAYS_OFFPEAK = "holidays_offpeak"

# Strategies
STRATEGY_FIXED = "fixed"
STRATEGY_TOU = "time_of_use"

# Error Codes
ERROR_INVALID_TIME_FORMAT = "invalid_time_format"
ERROR_SAME_START_END = "same_start_end"
ERROR_NEGATIVE_PRICE = "negative_price"