import asyncio

from globals import Globals
from lifx_device_set import LifxDeviceSet
from midi_handler import MidiHandler


async def main() -> None:
    midi_in = MidiHandler()
    if not await midi_in.is_midi_input_working():
        return

    device_set = LifxDeviceSet()
    device_set.devices = await device_set.discover_devices(0.5)

    await Globals.router.set_receiving(True)
    asyncio.create_task(Globals.router.start_receiving())
    asyncio.create_task(midi_in.start_receiving())
    asyncio.create_task(device_set.start_transmitting_converter_hue_to_all_devices())

    await asyncio.sleep(30)
    await midi_in.stop_receiving()
    await device_set.async_set_transmitting(False)

    print('Shutting down...')
    await asyncio.create_task(Globals.router.set_receiving(False))


if __name__ == "__main__":
    asyncio.run(main())
