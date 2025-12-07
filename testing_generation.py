import music21
import numpy as np
from testing_extraction import get_score, extract_chords, extract_notes
from music21.stream import Score
from music21.duration import Duration

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

def generate_chord_score(chord_sequence: np.ndarray[tuple[int]], duration_TM: np.ndarray, index_to_duration: dict[int, float], duration_to_index: dict[int, float], chord_to_index: dict[tuple[int], int]) -> Score:
    """
    Create a music21 Score from a sequence of chords and their durations.
    
    :param chord_sequence: Generated sequence of chords in MIDI numbers.
    :type chord_sequence: np.ndarray[tuple[int]]
    :param chord_duration_TM: Transition matrix for chord durations.
    :type chord_duration_TM: np.ndarray[[], dtype=float]
    :return: A music21 Score object representing the chord sequence.
    :rtype: Score
    """
    chord_score = Score()
    prev_duration = None
    for chord in chord_sequence:
        c = music21.chord.Chord()

        duration = generate_duration(duration_TM, index_to_duration, duration_to_index, prev_duration)
        c.duration = duration
        prev_duration = duration.quarterLength

        for midi_pitch in chord:
            n = music21.note.Note(midi=midi_pitch)
            c.add(n)
        chord_score.append(c)
    return chord_score 


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
    score = get_score('./MIDI_files/TSwift_BTD.mid')
    chord_TM, duration_TM, chord_to_index, index_to_chord, duration_to_index, index_to_duration = extract_chords(score)
    note_TM, note_to_index, index_to_note = extract_notes(score)

    current_chord_sequence = generate_sequence(chord_TM, index_to_chord, length=50)
    chord_score = generate_chord_score(current_chord_sequence, duration_TM, index_to_duration, duration_to_index, chord_to_index)
    chord_score.show('midi')

if __name__ == '__main__':
    main()