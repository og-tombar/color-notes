import asyncio
from enum import Enum

import rtmidi
from rtmidi.midiutil import open_midiinput

from globals import Globals
from notes_to_hue_converter import MidiNote


class MidiHandler:
    class MidiMessageType(Enum):
        NOTE_OFF = 128
        NOTE_ON = 144
        MODE_CHANGE = 176
        CHANNEL_AFTERTOUCH = 208

    class CCNumber(Enum):
        SUSTAIN = 64

    def __init__(self):
        self.lock = asyncio.Lock()
        self.midi_in = None
        self.is_receiving = False

    async def open_midi_input(self, midi_input_index: int = 0) -> bool:
        print('Attempting to open MIDI input...')
        async with self.lock:
            try:
                self.midi_in = open_midiinput(midi_input_index)[0]
                self.is_receiving = True
                print('MIDI input opened successfully.')
                return True
            except (EOFError, KeyboardInterrupt, rtmidi.NoDevicesError) as e:
                print('Error while trying to open MIDI input:')
                print(e)
                return False

    async def close_midi_input(self) -> None:
        print('Attempting to close MIDI input...')
        self.midi_in.close_port()
        del self.midi_in
        print('MIDI input closed successfully.')

    async def is_midi_input_working(self) -> bool:
        if await self.open_midi_input():
            await self.close_midi_input()
            return True
        else:
            return False

    async def start_receiving(self) -> None:
        if not await self.open_midi_input():
            return
        print("Entering main loop. Press Control-C to exit.")
        while self.is_receiving:
            message = self.midi_in.get_message()
            if message is not None:
                asyncio.create_task(self.process_message(message[0]))
            await asyncio.sleep(0)

    async def process_message(self, message: list[int]) -> None:
        message_type = message[0]
        match message_type:
            case MidiHandler.MidiMessageType.NOTE_ON.value:
                _, pitch, velocity = message
                if velocity == 0:
                    await Globals.converter.remove_note(pitch=message[1])
                else:
                    await Globals.converter.add_note(MidiNote(pitch=pitch, velocity=velocity))

            case MidiHandler.MidiMessageType.NOTE_OFF.value:
                await Globals.converter.remove_note(pitch=message[1])

            case MidiHandler.MidiMessageType.MODE_CHANGE.value:
                _, cc, value = message
                match cc:
                    case MidiHandler.CCNumber.SUSTAIN.value:
                        await Globals.converter.set_sustain(value=value)

            case MidiHandler.MidiMessageType.CHANNEL_AFTERTOUCH.value:
                pass

    async def stop_receiving(self) -> None:
        async with self.lock:
            self.is_receiving = False
            await self.close_midi_input()
