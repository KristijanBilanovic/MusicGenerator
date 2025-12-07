import numpy as np
import music21
from music21 import chord, note

def extract_chords(score):
    """
    Return's a list of chords and transition probability matrix
    
    :param score: score of notes
    """
    chord_stream = score.chordify()

    chords_to_index = {}
    index = 0

    for current_chord in chord_stream.recurse().getElementsByClass(chord.Chord):
        pitches = tuple(sorted(p.midi for p in current_chord.pitches))
        if pitches not in chords_to_index:
            chords_to_index[pitches] = index
            index += 1
    
    N = len(list(chords_to_index.keys()))

    chord_T_matrix = np.zeros((N, N), dtype=float)

    prev = None
    for c in chord_stream.recurse().getElementsByClass(chord.Chord):
        curr = tuple(sorted(p.midi for p in c.pitches))
        if prev is not None:
            x = chords_to_index[prev]
            y = chords_to_index[curr]
            chord_T_matrix[x, y] += 1
        prev = curr
    
    for row in chord_T_matrix:
        row_sum = row.sum()
        if row_sum > 0:
            row /= row_sum

    index_to_chords = {i : c for c, i in chords_to_index.items()}

    return chord_T_matrix, chords_to_index, index_to_chords

def extract_notes(score):
    """
    Extract notes from the main melody of the score.
    
    :param score: score of notes
    """
    melody_part = None

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
    TM, n = extract_chords(score)

    print(TM)

if __name__ == '__main__':
    main()