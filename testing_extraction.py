import music21
from music21 import chord, note

def extract_chords(score):
    """
    Return's a list of chords and transition probability matrix
    
    :param score: score of notes
    """
    chord_stream = score.chordify()
    chord_list = []

    for current_chord in chord_stream.recurse().getElementsByClass(chord.Chord):
        pitches = tuple(sorted(p.midi for p in current_chord.pitches))
        if pitches not in chord_list:
            chord_list.append(pitches)
    
    chord_T_matrix = [[0 for _ in range(len(chord_list))] for _ in range(len(chord_list))]
    prev_chord = None

    for i, current_chord in enumerate(chord_stream.recurse().getElementsByClass(chord.Chord)):
        if i > 0:
            x = chord_list.index(tuple(sorted(p.midi for p in prev_chord.pitches)))
            y = chord_list.index(tuple(sorted(p.midi for p in current_chord.pitches)))
            chord_T_matrix[x][y] += 1
        prev_chord = current_chord
    
    for i, row in enumerate(chord_T_matrix):
        row_sum = sum(row)
        if row_sum > 0:
            for j in range(len(row)):
                chord_T_matrix[i][j] /= row_sum

    return chord_T_matrix, chord_list

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

    notes_list = []

    for n in melody_part.recurse().getElementsByClass(note.Note):
        note_tuple = tuple([n.nameWithOctave, n.quarterLength])

        if note_tuple not in notes_list:
            notes_list.append(note_tuple)
    
    note_T_matrix = [[0] * len(notes_list) for _ in range(len(notes_list))]
    prev_note = None

    for i, current_note in enumerate(melody_part.recurse().getElementsByClass(note.Note)):
        if i > 0:
            x = notes_list.index(tuple([prev_note.nameWithOctave, prev_note.quarterLength]))
            y = notes_list.index(tuple([current_note.nameWithOctave, current_note.quarterLength]))
            note_T_matrix[x][y] += 1
        prev_note = current_note
    
    for i, row in enumerate(note_T_matrix):
        row_sum = sum(row)
        if row_sum > 0:
            for j in range(len(row)):
                note_T_matrix[i][j] /= row_sum
    
    return note_T_matrix, notes_list
    

def main():
    dir_path = input('Enter MIDI file path: ')
    score = music21.converter.parse(dir_path)
    TM, n = extract_notes(score)

    for row in TM:
        print(row)

if __name__ == '__main__':
    main()