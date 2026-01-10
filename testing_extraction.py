import numpy as np
import os
import music21
from music21 import chord, note
from music21.stream import Score, Part, Opus

def _get_all_chords_durations(scores: list[Score | Part | Opus]):
    all_chords = set()
    all_durations = set()

    for score in scores:
        for current_chord in score.recurse().getElementsByClass(chord.Chord):
            pitches = tuple(sorted(p.midi for p in current_chord.pitches))
            all_chords.add(pitches)
            all_durations.add(current_chord.duration.quarterLength)

    chords_to_index = {c: i for i, c in enumerate(all_chords)}
    duration_to_index = {d: i for i, d in enumerate(all_durations)}

    return chords_to_index, duration_to_index

def extract_chords(scores: list[Score | Part | Opus]):
    """
    Return's a list of chords and transition probability matrix
    
    :param score: score of notes
    """

    chords_to_index, duration_to_index = _get_all_chords_durations(scores)

    
    N_chords = len(list(chords_to_index.keys()))
    N_durations = len(list(duration_to_index.keys()))

    chords_TM = np.zeros((N_chords, N_chords), dtype=float)
    duration_TM = np.zeros((N_durations, N_durations), dtype=float)

    for score in scores:
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

def extract_notes(scores: list[Score | Part | Opus]):
    """
    Extract notes from the main melody of the score.
    
    :param score: score of notes
    """
    melody_parts: list[Score] = []
    
    for score in scores:
        for part in score.parts:
            if any(n.lyric for n in part.recurse().getElementsByClass(note.Note)):
                melody_parts.append(part)
                break

    note_to_index = {}
    index = 0

    for melody_part in melody_parts:
        for n in melody_part.recurse().getElementsByClass(note.Note):
            note_tuple = tuple([n.nameWithOctave, n.quarterLength])
            if note_tuple not in note_to_index:
                note_to_index[note_tuple] = index
                index += 1
    
    N = len(note_to_index.keys())

    note_T_matrix = np.zeros((N, N), dtype=float)

    for melody_part in melody_parts:
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
    return_list = []

    path = os.fsencode(dir_path)
    for file in os.listdir(path):
        filename = os.fsdecode(file)
        if filename.endswith('.mid') or filename.endswith('.midi'):
            print(f'Parsing file: {filename}')
            midi_path = os.path.join(dir_path, filename)
            score = music21.converter.parse(midi_path)
            return_list.append(score)

    return return_list

def partition_by_instrument(scores: list[Score | Part | Opus]) -> list[Score | Part | Opus]:
    partitioned_scores = []

    for score in scores:
        partitioned_score = music21.instrument.partitionByInstrument(score)
        partitioned_scores.append(partitioned_score)

    return partitioned_scores

def get_all_instruments(scores: list[Score | Part | Opus]) -> list[str]:
    instruments = set()

    for score in scores:
        for part in score.parts:
            instr = part.getInstrument()
            instruments.add(instr.instrumentName)

    return list(instruments)

def main():
    dir_path = input('Enter MIDI file path: ')
    scores = get_score(dir_path)
    scores = partition_by_instrument(scores)
    instruments = get_all_instruments(scores)
    print(len(instruments), 'instruments found:')


if __name__ == '__main__':
    main()