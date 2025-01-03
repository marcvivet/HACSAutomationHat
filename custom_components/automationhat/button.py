from asyncio import sleep, to_thread

from homeassistant.components.button import ButtonEntity

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

import automationhat as ah

from . import AHConfigEntry
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: AHConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add sensors for passed config_entry in HA."""
    hat = config_entry.runtime_data
    async_add_entities([
        RelayPush(hat, "one"),
        RelayPush(hat, "two"),
        RelayPush(hat, "three")])


class RelayPush(ButtonEntity):
    """Representation of a sensor."""

    def __init__(self, device, number) -> None:
        """Initialize the sensor."""
        self._state = True
        self._device = device
        self._number = number
        self._attr_unique_id = f"{self._device.hat_id}_relay_{number}"
        self._attr_name = f"Push Relay {number}"
        self._interval = device.data.get("push_interval", 1)

    @property
    def icon(self) -> str | None:
        """Icon of the entity."""
        return "mdi:gesture-tap"

    async def async_press(self) -> None:
        """Press the button."""
        relay = getattr(ah.relay, self._number)
        await self._device.set_relay_on(self._number)
        await to_thread(relay.on)
        await sleep(self._interval)
        await to_thread(relay.off)
        await self._device.set_relay_off(self._number)
        await sleep(self._interval)
        await to_thread(relay.light_no.write, 0)
        await to_thread(relay.light_nc.write, 0)

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
        """Return True if device is available."""
        return self._device.online

    async def async_added_to_hass(self):
        """Run when this Entity has been added to HA."""
        # Sensors should also register callbacks to HA when their state changes
        self._device.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Entity being removed from hass."""
        # The opposite of async_added_to_hass. Remove any registered call backs here.
        self._device.remove_callback(self.async_write_ha_state)

    @property
    def device_info(self):
        return self._device.device_info
