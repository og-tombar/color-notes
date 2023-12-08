import time
import asyncio
from globals import Globals
from lifx_device_set import LifxDeviceSet


class Tests:
    device_set = LifxDeviceSet()

    @staticmethod
    async def test_get_all_labels() -> tuple:
        return await Tests.device_set.all_devices_get('label')

    @staticmethod
    async def test_turn_on() -> tuple:
        return await Tests.device_set.all_devices_do('turn_on')

    @staticmethod
    async def test_turn_off() -> tuple:
        return await Tests.device_set.all_devices_do('turn_off')

    @staticmethod
    async def test_toggle_power() -> tuple:
        return await Tests.device_set.all_devices_do('toggle_power')

    @staticmethod
    async def test_get_all_colors() -> tuple:
        return await Tests.device_set.all_devices_get('color')

    @staticmethod
    async def test_set_color_default() -> tuple:
        return await Tests.device_set.all_devices_do('set_color')

    @staticmethod
    async def test_set_color_saturation_0() -> tuple:
        return await Tests.device_set.all_devices_do('set_color', {'saturation': 0})

    @staticmethod
    async def test_set_color_brightness_half() -> tuple:
        return await Tests.device_set.all_devices_do('set_color', {'brightness': 0.5})

    @staticmethod
    async def test_set_color_kelvin_3000() -> tuple:
        return await Tests.device_set.all_devices_do('set_color', {'kelvin': 3000})

    @staticmethod
    async def test_cycle_color_wheel() -> tuple:
        start_time = time.time()
        for i in range(100):
            print(i)
            await asyncio.sleep(0.05)
            await Tests.device_set.all_devices_do('set_color', {'hue': 180 * (i % 2)})
        print((time.time() - start_time) / 360)
        return {'result': True},


async def run_tests():
    print(await Tests.test_get_all_labels())
    # await Tests.test_turn_on()
    # await Tests.test_turn_off()
    # await Tests.test_toggle_power()
    # await Tests.test_set_color_default()
    # await Tests.test_set_color_saturation_0()
    # await Tests.test_set_color_brightness_half()
    # await Tests.test_set_color_kelvin_3000()
    # await Tests.test_cycle_color_wheel()


async def main():
    # init
    await Globals.router.set_receiving(True)
    Tests.device_set.devices = await Tests.device_set.discover_devices(0.5)
    asyncio.create_task(Globals.router.start_receiving())

    # tests
    await run_tests()

    # shut down
    await asyncio.create_task(Globals.router.set_receiving(False))

if __name__ == "__main__":
    asyncio.run(main())
