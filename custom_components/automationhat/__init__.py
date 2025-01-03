"""The Detailed Hello World Push integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .automation_hat import AutomationHat


PLATFORMS = [
    Platform.BUTTON,
    Platform.SWITCH,
    Platform.LIGHT]

type AHConfigEntry = ConfigEntry[AutomationHat]


async def async_setup_entry(hass: HomeAssistant, entry: AHConfigEntry) -> bool:
    entry.runtime_data = AutomationHat(hass, entry.data)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    return unload_ok
