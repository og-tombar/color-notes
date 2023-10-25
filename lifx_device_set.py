import asyncio
import time

from globals import Globals
from lifx_device import LifxDevice


class LifxDeviceSet:
    PORT = 56700

    def __init__(self):
        print('Initializing LIFX Device Set')
        self.devices: list[LifxDevice] = []

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

    async def all_devices_do(self, method: str = 'set_power', args: dict = None) -> tuple:
        return await asyncio.gather(*[device.do(method, args) for device in self.devices])

    async def all_devices_get(self, prop: str = 'service') -> tuple:
        return await asyncio.gather(*[device.get(prop) for device in self.devices])

    async def test_get_all_labels(self):
        return await self.all_devices_get('label')

    async def test_turn_on(self):
        return await self.all_devices_do('turn_on')

    async def test_turn_off(self):
        return await self.all_devices_do('turn_off')

    async def test_toggle_power(self):
        return await self.all_devices_do('toggle_power')

    async def test_get_all_colors(self):
        return await self.all_devices_get('color')

    async def test_set_color_default(self):
        return await self.all_devices_do('set_color')

    async def test_set_color_saturation_0(self):
        return await self.all_devices_do('set_color', {'saturation': 0})

    async def test_set_color_brightness_half(self):
        return await self.all_devices_do('set_color', {'brightness': 0.5})

    async def test_set_color_kelvin_3000(self):
        return await self.all_devices_do('set_color', {'kelvin': 3000})

    async def test_cycle_color_wheel(self):
        start_time = time.time()
        for i in range(100):
            print(i)
            await asyncio.sleep(0.05)
            await self.all_devices_do('set_color', {'hue': 180 * (i % 2)})
        print((time.time() - start_time) / 360)
        return {'result': True}
