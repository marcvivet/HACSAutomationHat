from __future__ import annotations

import asyncio
from asyncio import to_thread
import random
from typing import Callable

from homeassistant.core import HomeAssistant

import automationhat as ah

from .const import DOMAIN


class AutomationHat:

    def __init__(self, hass: HomeAssistant, data: dict) -> None:
        """Init AutomationHat roller."""
        self._id = "automationhat"
        self._name = "Automation Hat"
        self._model = "PIM213"
        self._manufacturer = "Pimoroni"
        self._online = True
        self._data = data

        self._callbacks = set()
        self._loop = asyncio.get_event_loop()

        self._relay_state = {
            "one": False,
            "two": False,
            "three": False
        }

        self._light_state = {
            "power": False,
            "comm": False,
            "warn": False
        }

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._id)},
            "name": self._name,
            "manufacturer": self._manufacturer,
            "model": self._model,
        }

    @property
    def manufacturer(self) -> str:
        return self._manufacturer

    @property
    def online(self) -> str:
        return self._online

    @property
    def model(self) -> str:
        return self._model

    @property
    def name(self) -> str:
        return self._name

    @property
    def data(self) -> dict:
        return self._data

    @property
    def hat_id(self) -> str:
        """Return ID for roller."""

        return self._id

    async def test_hat(self) -> bool:
        try:
            await to_thread(ah.setup)
        except Exception:
            return False
        return True

    async def set_relay_on(self, number) -> None:
        self._relay_state[number] = True
        await self.publish_updates()

    async def get_relay_state(self, number) -> bool:
        return self._relay_state[number]

    async def set_relay_off(self, number) -> None:
        """Publish updates, with a random delay to emulate interaction with device."""
        self._relay_state[number] = False
        await self.publish_updates()

    async def set_light_on(self, number) -> None:
        self._light_state[number] = True
        await self.publish_updates()

    async def get_light_state(self, number) -> bool:
        return self._light_state[number]

    async def set_light_off(self, number) -> None:
        """Publish updates, with a random delay to emulate interaction with device."""
        self._light_state[number] = False
        await self.publish_updates()

    def register_callback(self, callback: Callable[[], None]) -> None:
        """Register callback, called changes state."""
        self._callbacks.add(callback)

    def remove_callback(self, callback: Callable[[], None]) -> None:
        """Remove previously registered callback."""
        self._callbacks.discard(callback)

    async def publish_updates(self) -> None:
        """Schedule call all registered callbacks."""
        for callback in self._callbacks:
            callback()

    @property
    def online(self) -> float:
        """Automation hat is online."""
        return True
