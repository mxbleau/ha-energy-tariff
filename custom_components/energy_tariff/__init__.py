"""The Energy Tariff integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PLATFORMS
from homeassistant.core import HomeAssistant

PLATFORMS: list[str] = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Energy Tariff from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)