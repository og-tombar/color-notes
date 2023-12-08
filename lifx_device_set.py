import asyncio
import time

from globals import Globals
from lifx_device import LifxDevice


class LifxDeviceSet:
    PORT = 56700

    def __init__(self):
        print('Initializing LIFX Device Set')
        self.lock = asyncio.Lock()
        self.devices: list[LifxDevice] = []
        self.is_transmitting: bool = False
        self.current_hue: float = 0

    @property
    async def info(self) -> str:
        device_set_info = '\nLIFX Device Set:\n'
        devices_info = await asyncio.gather(*[device.get('info') for device in self.devices])
        for i, info in enumerate(devices_info):
            device_set_info += f'\nLIFX Device [{i+1}]:'
            device_set_info += f'\n{info}'
        return device_set_info

    async def discover_devices(self, discovery_timeout: float = 2) -> list[LifxDevice]:
        print(f'Initiating async discovery for {discovery_timeout} seconds...')
        responses = await Globals.router.discover_devices(discovery_timeout)
        responses = sorted(responses.items(), key=lambda res: res[1]['label'])
        devices = [LifxDevice(address) for address, res in responses]
        print(f'Async discovery completed.')
        return devices

    async def async_set_transmitting(self, transmitting: bool = True):
        async with self.lock:
            self.is_transmitting = transmitting

    async def all_devices_do(self, method: str = 'set_power', args: dict = None) -> tuple:
        return await asyncio.gather(*[device.do(method, args) for device in self.devices])

    async def all_devices_get(self, prop: str = 'service') -> tuple:
        return await asyncio.gather(*[device.get(prop) for device in self.devices])

    async def start_transmitting_converter_hue_to_all_devices(self) -> None:
        await self.async_set_transmitting(True)
        while self.is_transmitting:
            new_hue = await Globals.converter.async_get_current_hue()
            if new_hue == self.current_hue:
                await asyncio.sleep(0)
            elif new_hue == -1:
                await self.all_devices_do('set_color', {'saturation': 0, 'kelvin': 5000})
            else:
                await self.all_devices_do('set_color', {'saturation': 1, 'hue': new_hue})
            async with self.lock:
                self.current_hue = new_hue
