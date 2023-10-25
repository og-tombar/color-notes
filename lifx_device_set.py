import asyncio

from globals import Globals
from lifx_device import LifxDevice


class LifxDeviceSet:
    PORT = 56700

    def __init__(self):
        print('Initializing LIFX Device Set')
        self.devices: list[LifxDevice] = []

    @property
    async def info(self) -> str:
        info = '\nLIFX Device Set:'
        for i, d in enumerate(self.devices):
            info += f'\n{str(i+1)}. {await d.info}'
        return info

    async def discover_devices(self, discovery_timeout: float = 2) -> list[LifxDevice]:
        print(f'Initiating async discovery for {discovery_timeout} seconds...')
        responses = await Globals.router.discover_devices(discovery_timeout)
        responses = sorted(responses.items(), key=lambda res: res[1])
        devices = [LifxDevice(address) for address, res in responses]
        print(f'Async discovery completed.')
        return devices

    async def all_devices_do(self, method: str = 'set_power', args: tuple = ()) -> tuple:
        return await asyncio.gather(*[device.do(method, args) for device in self.devices])

    async def all_devices_get(self, prop: str = 'service') -> tuple:
        return await asyncio.gather(*[device.get(prop) for device in self.devices])

    async def test1(self):
        return await self.all_devices_get('label')

    async def test2(self):
        return await self.all_devices_do('turn_on')

    async def test3(self):
        return await self.all_devices_do('turn_off')

    async def test4(self):
        return await self.all_devices_do('toggle_power')
