from asyncio import to_thread

from homeassistant.components.switch import SwitchEntity

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

import automationhat as ah

from . import HubConfigEntry
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: HubConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add sensors for passed config_entry in HA."""
    hub = config_entry.runtime_data
    async_add_entities([
        RelaySwitch(hub.automationhat, "one"),
        RelaySwitch(hub.automationhat, "two"),
        RelaySwitch(hub.automationhat, "three")])


class RelaySwitch(SwitchEntity, RestoreEntity):
    """Representation of a relay switch."""

    def __init__(self, device, number) -> None:
        """Initialize the switch."""
        self._state = None  # Use None to handle initial unknown state
        self._device = device
        self._number = number
        self._attr_unique_id = f"{self._device._id}_switch_{number}"
        self._attr_name = f"Relay {number}"

    @property
    def icon(self) -> str | None:
        """Icon of the entity."""
        return "mdi:toggle-switch-variant" if self.is_on else "mdi:toggle-switch-variant-off"

    @property
    def is_on(self):
        """Return the on/off state."""
        return self._state

    async def async_turn_on(self):
        """Turn the switch on."""
        relay = getattr(ah.relay, self._number)
        await self._device.set_relay_on(self._number)
        await to_thread(relay.on)
        self._state = True
        self.async_write_ha_state()

    async def async_turn_off(self):
        """Turn the switch off."""
        relay = getattr(ah.relay, self._number)
        await self._device.set_relay_off(self._number)
        await to_thread(relay.off)
        self._state = False
        self.async_write_ha_state()

    async def async_update(self):
        """Fetch the current state from the device."""
        self._state = await self._device.get_relay_state(self._number)

    async def async_added_to_hass(self):
        """Run when this Entity has been added to HA."""
        await super().async_added_to_hass()
        # Restore the state if possible
        if (restored_state := await self.async_get_last_state()) is not None:
            self._state = restored_state.state == "on"
        else:
            # If no restored state, query the device for its current state
            await self.async_update()

    @property
    def should_poll(self) -> bool:
        """Polling is not needed as we rely on callbacks."""
        return False

    @property
    def available(self) -> bool:
        """Return True if the device and hub are available."""
        return self._device.online and self._device.hub.online