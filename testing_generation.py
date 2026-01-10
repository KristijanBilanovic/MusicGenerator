import music21
import numpy as np
from testing_extraction import get_score, extract_chords, extract_notes
from music21.stream import Score, Part
from music21.duration import Duration
from music21 import note
import random

def generate_sequence(transition_matrix: np.ndarray, index_to_state: dict[int, tuple[int]], length: int = 100):
    """
    Generate a Markov state sequence based on the transition matrix.
    :param transition_matrix: transition matrix for chords
    :param index_to_state: mapping from indices to chords
    :param length: length of the generated sequence
    """

    chord_sequence = []

    N = transition_matrix.shape[0]
    
    current_chord_index = np.random.choice(N)
    chord_sequence.append(index_to_state[current_chord_index])

    for _ in range(length - 1):
        if transition_matrix[current_chord_index].sum() == 0:
            break
        next_chord_index = np.random.choice(N, p=transition_matrix[current_chord_index])
        chord_sequence.append(index_to_state[next_chord_index])
        current_chord_index = next_chord_index

    return np.array(chord_sequence, dtype=object)

def generate_chord_score(chord_sequence: np.ndarray[tuple[int]], duration_TM: np.ndarray, index_to_duration: dict[int, float], duration_to_index: dict[int, float], chord_to_index: dict[tuple[int], int]) -> Part:
    """
    Create a music21 Score from a sequence of chords and their durations.
    
    :param chord_sequence: Generated sequence of chords in MIDI numbers.
    :type chord_sequence: np.ndarray[tuple[int]]
    :param chord_duration_TM: Transition matrix for chord durations.
    :type chord_duration_TM: np.ndarray[[], dtype=float]
    :return: A music21 Score object representing the chord sequence.
    :rtype: Score
    """
    chord_score = Part()
    prev_duration = None
    for chord in chord_sequence:
        if random.random() < 0.8:  # 80% chance
            r = note.Rest(0.5)
            chord_score.append(r)

        c = music21.chord.Chord()

        duration = generate_duration(duration_TM, index_to_duration, duration_to_index, prev_duration)
        c.duration = duration
        prev_duration = duration.quarterLength

        for midi_pitch in chord:
            n = music21.note.Note(midi=midi_pitch)
            c.add(n)
        chord_score.append(c)
    return chord_score 

def generate_note_score(note_sequence: np.ndarray[tuple[int, int]], note_to_index: dict[tuple[str, float], int], index_to_note: dict[int, tuple[str, float]]) -> Part:
    """
    Create a music21 Score from a sequence of notes.
    
    :param note_sequence: Generated sequence of notes (nameWithOctave, duration).
    :type note_sequence: np.ndarray[tuple[int, int]]
    :return: A music21 Score object representing the note sequence.
    :rtype: Part
    """
    note_score = Part()
    for note_tuple in note_sequence:
        if random.random() < 0.4:  # 30% chance
            r = note.Rest(0.5)
            note_score.append(r)
        n = music21.note.Note()
        n.nameWithOctave = note_tuple[0]
        n.duration = Duration(quarterLength=note_tuple[1])
        note_score.append(n)
    return note_score

def generate_duration(duration_TM, index_to_duration, duration_to_index, prev_duration) -> Duration:
    """
    Generate a random duration for a chord.
    :return: A music21 Duration object.
    :rtype: Duration
    """
    if prev_duration is None:
        duration_index = np.random.choice(len(index_to_duration))
    else:
        duration_index = np.random.choice(len(index_to_duration), p=duration_TM[duration_to_index[prev_duration]])
    duration_value = index_to_duration[duration_index]
    return Duration(quarterLength=duration_value)


def main():
    score = get_score('./MIDI_files')
    chord_TM, duration_TM, chord_to_index, index_to_chord, duration_to_index, index_to_duration = extract_chords(score)
    note_TM, note_to_index, index_to_note = extract_notes(score)

    generated_chord_sequence = generate_sequence(chord_TM, index_to_chord, length=50)
    chord_score = generate_chord_score(generated_chord_sequence, duration_TM, index_to_duration, duration_to_index, chord_to_index)

    generated_note_sequence = generate_sequence(note_TM, index_to_note, length=100)
    note_score = generate_note_score(generated_note_sequence, note_to_index, index_to_note)

    combined_score = Score()
    combined_score.append(chord_score)
    combined_score.append(note_score)

    combined_score.show('midi')

if __name__ == '__main__':
    main()