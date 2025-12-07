import numpy as np
import music21
from music21 import chord, note
from music21.stream import Score, Part, Opus

def extract_chords(score: Score | Part | Opus):
    """
    Return's a list of chords and transition probability matrix
    
    :param score: score of notes
    """

    chords_to_index = {}
    duration_to_index = {}

    index_chords = 0
    index_duration = 0

    # map chords and durations to indices
    for current_chord in score.recurse().getElementsByClass(chord.Chord):
        duration = current_chord.duration.quarterLength
        pitches = tuple(sorted(p.midi for p in current_chord.pitches))
        if pitches not in chords_to_index:
            chords_to_index[pitches] = index_chords
            index_chords += 1
        if duration not in duration_to_index:
            duration_to_index[duration] = index_duration
            index_duration += 1
    
    N_chords = len(list(chords_to_index.keys()))
    N_durations = len(list(duration_to_index.keys()))

    chords_TM = np.zeros((N_chords, N_chords), dtype=float)
    duration_TM = np.zeros((N_durations, N_durations), dtype=float)

    prev = None
    for c in score.recurse().getElementsByClass(chord.Chord):
        curr = tuple(sorted(p.midi for p in c.pitches))
        
        if prev is not None:
            x = chords_to_index[tuple(sorted(p.midi for p in prev.pitches))]
            y = chords_to_index[curr]
            chords_TM[x, y] += 1

            x = duration_to_index[prev.duration.quarterLength]
            y = duration_to_index[c.duration.quarterLength]
            duration_TM[x, y] += 1

        prev = c
    
    for row in chords_TM:
        row_sum = row.sum()
        if row_sum > 0:
            row /= row_sum

    for row in duration_TM:
        row_sum = row.sum()
        if row_sum > 0:
            row /= row_sum

    index_to_chords = {i : c for c, i in chords_to_index.items()}
    index_to_duration = {i : d for d, i in duration_to_index.items()}

    return chords_TM, duration_TM, chords_to_index, index_to_chords, duration_to_index, index_to_duration

def extract_notes(score):
    """
    Extract notes from the main melody of the score.
    
    :param score: score of notes
    """
    melody_part: Score = Score()

    for part in score.parts:
        if any(n.lyric for n in part.recurse().getElementsByClass(note.Note)):
            melody_part = part
            break

    note_to_index = {}
    index = 0

    for n in melody_part.recurse().getElementsByClass(note.Note):
        note_tuple = tuple([n.nameWithOctave, n.quarterLength])
        if note_tuple not in note_to_index:
            note_to_index[note_tuple] = index
            index += 1
    
    N = len(note_to_index.keys())

    note_T_matrix = np.zeros((N, N), dtype=float)

    prev = None
    for c in melody_part.recurse().getElementsByClass(note.Note):
        curr = tuple([c.nameWithOctave, c.quarterLength])
        if prev is not None:
            x = note_to_index[prev]
            y = note_to_index[curr]
            note_T_matrix[x, y] += 1
        prev = curr
    
    for row in note_T_matrix:
        row_sum = row.sum()
        if row_sum > 0:
            row /= row_sum
    
    index_to_note = {i : n for n, i in note_to_index.items()}
    
    return note_T_matrix, note_to_index, index_to_note

def get_score(dir_path):
    """
    Get music21 score from MIDI file.
    
    :param dir_path: path to MIDI file
    """
    score = music21.converter.parse(dir_path)
    return score

def main():
    dir_path = input('Enter MIDI file path: ')
    score = get_score(dir_path)
    TM1, TM2, n, k, t, r = extract_chords(score)


if __name__ == '__main__':
    main()