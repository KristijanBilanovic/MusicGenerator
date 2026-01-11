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
            music21_instr = music21.instrument.fromString(instr_name)

            generated_sequence = model.generate_sequence(length=length)
            part = music21.stream.Part()
            for note_name in generated_sequence:
                note = music21.note.Note(midi=note_name)
                note.storedInstrument = music21_instr
                part.append(note)
            part.makeMeasures()
            new_score.append(part)
            new_score.makeMeasures()
            
        new_score.show('midi')