import copy
import time


class Note:
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
        self.hue = Note.note_to_hue[pitch % 12]
        self.pedalled = False

    def __str__(self):
        s = f'Pitch: {self.pitch}\n'
        s += f'Velocity: {self.velocity}\n'
        s += f'Hue: {self.hue}\n'
        s += f'Pedalled: {self.pedalled}\n'
        return s


class Chord:
    def __init__(self, notes: list[Note]):
        self.notes = notes

    def __str__(self):
        s = 'Chord:\n'
        for note in self.notes:
            s += f'\n{note}'
        return s

    def distance_from_hue(self, hue: float) -> float:
        if len(self.notes) == 0:
            return -1
        return sum([abs(note.velocity * (hue - note.hue)) for note in self.notes])

    def weighted_average(self) -> float:
        if len(self.notes) == 0:
            return -1
        numerator = sum([note.hue * note.velocity for note in self.notes])
        denominator = sum([note.velocity for note in self.notes])
        return numerator / denominator

    def calc_best_hue(self) -> float:
        chord_copy = copy.deepcopy(self)
        chord_copy.notes.sort(key=lambda n: n.hue)

        best_hue = chord_copy.weighted_average()
        best_distance = chord_copy.distance_from_hue(best_hue)
        for note in chord_copy.notes:
            note.hue += 360
            new_hue = chord_copy.weighted_average()
            new_distance = chord_copy.distance_from_hue(new_hue)
            if new_distance < best_distance:
                best_hue = new_hue
                best_distance = new_distance
        return best_hue % 360
#
#
# chord1 = Chord([
#     Note(pitch=60, velocity=100),
#     Note(pitch=67, velocity=100)
# ])
# # print(chord1.weighted_average())
#
# chord2 = Chord([
#     Note(pitch=60, velocity=100),
#     Note(pitch=65, velocity=100)
# ])
# # print(chord2.calc_best_hue())
#
# start_time = time.time()
# chord3 = Chord([
#     Note(pitch=60, velocity=100),
#     Note(pitch=61, velocity=100),
#     Note(pitch=62, velocity=100),
#     Note(pitch=63, velocity=100),
#     Note(pitch=64, velocity=100),
#     Note(pitch=65, velocity=100),
#     Note(pitch=66, velocity=100),
#     Note(pitch=67, velocity=100),
#     Note(pitch=68, velocity=100),
#     Note(pitch=69, velocity=100),
#     Note(pitch=70, velocity=100),
#     Note(pitch=71, velocity=100),
# ])
# print(time.time() - start_time)
# print(chord3.calc_best_hue())
#
# chord4 = Chord([
#     Note(pitch=62, velocity=100),
#     Note(pitch=65, velocity=100)
# ])
# # print(chord4.calc_best_hue())
