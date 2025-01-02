from asyncio import to_thread

from homeassistant.components.switch import SwitchEntity

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

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


class RelaySwitch(SwitchEntity):
    """Representation of a sensor."""

    def __init__(self, device, number) -> None:
        """Initialize the sensor."""
        self._state = False
        self._device = device
        self._number = number
        self._attr_unique_id = f"{self._device._id}_switch_{number}"
        self._attr_name = f"Switch {number}"

    @property
    def icon(self) -> str | None:
        """Icon of the entity."""
        if self._state:
            return "mdi:toggle-switch-variant"
        return "mdi:toggle-switch-variant-off"

    @property
    def is_on(self):
        """Return is_on status."""
        return self._state

    async def async_turn_on(self):
        """Turn On method."""
        relay = getattr(ah.relay, self._number)
        self._state = True
        await self._device.set_relay_on(self._number)
        await to_thread(relay.on)

    async def async_turn_off(self):
        """Turn Off method."""
        relay = getattr(ah.relay, self._number)
        self._state = False
        await self._device.set_relay_off(self._number)
        await to_thread(relay.off)
        await to_thread(relay.light_no.write, 1)
        await to_thread(relay.light_nc.write, 0)

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    async def async_update(self):
        """Return sensor state."""
        return self._state

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._attr_name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return {"identifiers": {(DOMAIN, self._device._id)}}

    # This property is important to let HA know if this entity is online or not.
    # If an entity is offline (return False), the UI will refelect this.
    @property
    def available(self) -> bool:
        """Return True if roller and hub is available."""
        return self._device.online and self._device.hub.online

    async def async_added_to_hass(self):
        """Run when this Entity has been added to HA."""
        # Sensors should also register callbacks to HA when their state changes
        self._device.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Entity being removed from hass."""
        # The opposite of async_added_to_hass. Remove any registered call backs here.
        self._device.remove_callback(self.async_write_ha_state)
