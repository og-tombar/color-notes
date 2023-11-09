import asyncio
import copy


class MidiNote:
    note_to_hue: dict = {
        0: 0,       # C
        1: 210,     # C#
        2: 60,      # D
        3: 270,     # Eb
        4: 120,     # E
        5: 330,     # F
        6: 180,     # F#
        7: 30,      # G
        8: 240,     # Ab
        9: 90,      # A
        10: 300,    # Bb
        11: 150     # B
    }

    def __init__(self, pitch: int = 60, velocity: int = 100):
        self.pitch = pitch
        self.velocity = velocity
        self.hue = MidiNote.note_to_hue[pitch % 12]
        self.is_pedalled = False

    def __str__(self):
        s = f'Pitch: {self.pitch}\n'
        s += f'Velocity: {self.velocity}\n'
        s += f'Hue: {self.hue}\n'
        s += f'Pedalled: {self.is_pedalled}\n'
        return f'Pitch: {self.pitch} | Velocity: {self.velocity} | Hue: {self.hue} | Pedalled: {self.is_pedalled}'


class NotesToHueConverter:
    def __init__(self, notes: list[MidiNote] = None):
        self.lock: asyncio.Lock = asyncio.Lock()
        self.notes: list[MidiNote] = [] if notes is None else notes
        self.current_hue: float = 0
        self.sustain: int = 0

    def __str__(self):
        s = 'Notes:\n'
        for note in self.notes:
            s += f'{note}\n'
        return s

    async def async_get_current_hue(self):
        async with self.lock:
            return self.current_hue

    async def add_note(self, note: MidiNote) -> None:
        async with self.lock:
            is_note_in_converter = False
            for n in self.notes:
                if n.pitch == note.pitch:
                    n.velocity = note.velocity
                    n.is_pedalled = False
                    is_note_in_converter = True

            if not is_note_in_converter:
                self.notes.append(note)
        await self.convert()

    async def remove_note(self, pitch: int) -> None:
        async with self.lock:
            for n in self.notes:
                if n.pitch == pitch:
                    if self.sustain < 32:
                        self.notes.remove(n)
                    else:
                        n.is_pedalled = True
        await self.convert()

    async def set_sustain(self, value: int = 0) -> None:
        async with self.lock:
            self.sustain = value
            print(self.sustain)
            to_remove = []
            if self.sustain < 32:
                to_remove = [n for n in self.notes if n.is_pedalled]
        for n in to_remove:
            await self.remove_note(n.pitch)

    async def convert(self) -> float:
        async with self.lock:
            if len(self.notes) == 0:
                self.current_hue = -1
                return self.current_hue
            converter_copy = copy.deepcopy(self)
            converter_copy.lock = asyncio.Lock()
        converter_copy.notes.sort(key=lambda n: n.hue)
        best_hue = await converter_copy.weighted_average()
        best_distance = await converter_copy.distance_from_hue(best_hue)
        for note in converter_copy.notes:
            note.hue += 360
            new_hue = await converter_copy.weighted_average()
            new_distance = await converter_copy.distance_from_hue(new_hue)
            if new_distance < best_distance:
                best_hue = new_hue
                best_distance = new_distance
        async with self.lock:
            self.current_hue = best_hue % 360
            return self.current_hue

    async def weighted_average(self) -> float:
        async with self.lock:
            if len(self.notes) == 0:
                return 0
            numerator = sum([note.hue * note.velocity for note in self.notes])
            denominator = sum([note.velocity for note in self.notes])
            return numerator / denominator

    async def distance_from_hue(self, hue: float) -> float:
        async with self.lock:
            if len(self.notes) == 0:
                return 0
            return sum([abs(note.velocity * (hue - note.hue)) for note in self.notes])
