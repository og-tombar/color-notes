import asyncio

from globals import Globals
from lifx_device_set import LifxDeviceSet


async def main():
    device_set = LifxDeviceSet()
    device_set.devices = await device_set.discover_devices()

    await Globals.router.set_receiving(True)
    asyncio.create_task(Globals.router.start_receiving())

    await device_set.test4()
    print(await device_set.info)

    await asyncio.create_task(Globals.router.set_receiving(False))


if __name__ == "__main__":
    asyncio.run(main())
