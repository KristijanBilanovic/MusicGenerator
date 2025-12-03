import music21
from music21 import chord

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


def main():
    dir_path = input('Enter MIDI file path: ')
    score = music21.converter.parse(dir_path)
    T_matrix, chords = extract_chords(score)
    for row in T_matrix:
        print(row)

if __name__ == '__main__':
    main()