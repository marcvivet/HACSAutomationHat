"""A demonstration 'hub' that connects several devices."""
from __future__ import annotations

# In a real implementation, this would be in an external library that's on PyPI.
# The PyPI package needs to be included in the `requirements` section of manifest.json
# See https://developers.home-assistant.io/docs/creating_integration_manifest
# for more information.
# This dummy hub always returns 3 rollers.
import asyncio
import random
from typing import Callable

from homeassistant.core import HomeAssistant


class Hub:
    """Dummy hub for Hello World example."""

    manufacturer = "Demonstration Corp"

    def __init__(self, hass: HomeAssistant, host: str) -> None:
        """Init dummy hub."""
        self._host = host
        self._hass = hass
        self._name = host
        self._id = host.lower()
        self.automationhat = AutomationHat(f"{self._id}_automationhat", f"{self._name} AutomationHat", self)
        self.online = True

    @property
    def hub_id(self) -> str:
        """ID for dummy hub."""
        return self._id

    async def test_connection(self) -> bool:
        """Test connectivity to the Dummy hub is OK."""
        await asyncio.sleep(1)
        return True


class AutomationHat:

    def __init__(self, hatid: str, name: str, hub: Hub) -> None:
        """Init dummy roller."""
        self._id = hatid
        self.hub = hub
        self.name = name
        self._callbacks = set()
        self._loop = asyncio.get_event_loop()
        self._target_position = 100
        self._current_position = 100

        # Some static information about this device
        self.firmware_version = f"0.0.0"
        self.model = "AutomationHat Device"
        self._relay_state = {
            "one": False,
            "two": False,
            "three": False
        }

    @property
    def hat_id(self) -> str:
        """Return ID for roller."""
        return self._id

    async def set_relay_on(self, number) -> None:
        """
        Set dummy cover to the given position.

        State is announced a random number of seconds later.
        """
        self._relay_state[number] = True
        await self.publish_updates()

    async def get_relay_state(self, number) -> bool:
        """
        Set dummy cover to the given position.

        State is announced a random number of seconds later.
        """
        return self._relay_state[number]

    async def set_relay_off(self, number) -> None:
        """Publish updates, with a random delay to emulate interaction with device."""
        self._relay_state[number] = False
        await self.publish_updates()

    def register_callback(self, callback: Callable[[], None]) -> None:
        """Register callback, called when Roller changes state."""
        self._callbacks.add(callback)

    def remove_callback(self, callback: Callable[[], None]) -> None:
        """Remove previously registered callback."""
        self._callbacks.discard(callback)

    # In a real implementation, this library would call it's call backs when it was
    # notified of any state changeds for the relevant device.
    async def publish_updates(self) -> None:
        """Schedule call all registered callbacks."""
        for callback in self._callbacks:
            callback()

    @property
    def online(self) -> float:
        """Roller is online."""
        # The dummy roller is offline about 10% of the time. Returns True if online,
        # False if offline.
        return True
