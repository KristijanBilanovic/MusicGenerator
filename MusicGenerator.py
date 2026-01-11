import music21
import numpy as np
from MusicDataTrainer import MusicDataTrainer

class MusicGenerator:
    def __init__(self, data_path: str = 'MIDI_files', laplace_smoothing: float = 1.0):
        self._data_trainer = MusicDataTrainer(data_path=data_path)
        self._data_trainer.analyze_data(laplace_smoothing=laplace_smoothing)
        self._models_by_instrument = self._data_trainer.train_models()

    def generate_music(self, length: int = 20, laplace_smoothing: float = 1.0):
        new_score = music21.stream.Score()

        instruments = np.random.choice(list(self._models_by_instrument.keys()), size=4, replace=False)
        print(f"Generating music for instrument: {instruments}")

        for instr_name in instruments:
            model = self._models_by_instrument[instr_name]
            
            try:
                music21_instr = music21.instrument.fromString(instr_name)
            except music21.exceptions21.InstrumentException:
                music21_instr = music21.instrument.Piano()

            generated_sequence = model.generate_sequence(length=length)
            part = music21.stream.Part()
            for tm_index in generated_sequence:
                music_element = MusicDataTrainer.str_to_midi_tuple(tm_index)
                if len(music_element) > 1: 
                    c = music21.chord.Chord()
                    for midi_pitch in music_element:
                        n = music21.note.Note(midi=midi_pitch)
                        c.add(n)
                    c.storedInstrument = music21_instr
                    part.append(c)
                    continue
                elif len(music_element) == 1 and music_element[0] == -1:
                    r = music21.note.Rest()
                    part.append(r)
                    continue
                elif len(music_element) == 1:
                    note = music21.note.Note(midi=music_element[0])
                    note.storedInstrument = music21_instr
                    part.append(note)
            part.makeMeasures()
            new_score.append(part)
            new_score.makeMeasures()

        new_score.show('midi')