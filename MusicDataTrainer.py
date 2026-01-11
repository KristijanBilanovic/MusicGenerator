import os
import music21
import pandas as pd

class MusicDataTrainer:
    def __init__(self, data_path: str = 'MIDI_files'):
        self._data_path = data_path
        self._transition_matrices = {}
        self._starting_probabilities = {}
        self._scores = self._load_data()
        self.instrument_mapping = self._get_all_instruments()
        
    def _load_data(self) -> list[music21.stream.Score]:
        """
        Parse MIDI files from the given directory and partition them by instruments.
        :param input_path: Path to the directory containing MIDI files.
        :return: List of partitioned music21 Score objects.
        """
        scores = []

        for root, dirs, files in os.walk(self._data_path):
            for filename in files:
                if filename.lower().endswith('.mid') or filename.lower().endswith('.midi'):
                    midi_path = os.path.join(root, filename)
                    score = music21.converter.parse(midi_path)
                    partitioned_score = music21.instrument.partitionByInstrument(score)
                    scores.append(partitioned_score)
                
        return scores
    
    def _get_all_instruments(self) -> dict[str, int]:
        """
        Get a mapping of all unique instruments from the parsed scores to their indices.
        :return: Dict of instrument names mapped to their indices.
        """
        instrument_mapping = dict()
        index = 0

        for score in self._scores:
            for part in score.parts:
                instr = part.getInstrument()
                if instr.instrumentName not in instrument_mapping:
                    instrument_mapping[instr.instrumentName] = index
                    index += 1

        return instrument_mapping

    def analyze_data(self, laplace_smoothing: float = 1.0) -> None:
        """
        Creates parameters needed for a Markov Chain probabilistic model - transition matrices and starting probabilities.
        The models are NOT trained yet after running this method. For training, call the train_models() method.
        :return: None
        """
        transitions_by_instrument = {}
        initial_notes_by_instrument = {}

        # Find all transitions for each instrument
        for score in self._scores:
            for part in score.parts:
                instr = part.getInstrument()
                instr_name = instr.instrumentName

                notes = [note.pitch.midi for note in part.recurse() if isinstance(note, music21.note.Note)]

                if len(notes) < 2:
                    continue
                
                # Append initial notes (starting probabilities) for each instrument
                if instr_name not in initial_notes_by_instrument:
                    initial_notes_by_instrument[instr_name] = [notes[0]]
                else:
                    initial_notes_by_instrument[instr_name].append(notes[0])

                # Pairs of (current_note, next_note)
                transition_pairs = list(zip(notes[:-1], notes[1:]))

                if instr_name not in transitions_by_instrument:
                    transitions_by_instrument[instr_name] = transition_pairs
                else:
                    transitions_by_instrument[instr_name].extend(transition_pairs)
        
        # Remove instruments with no transitions
        keys_to_remove = [k for k, v in transitions_by_instrument.items() if len(v) == 0]

        for k in keys_to_remove:
            transitions_by_instrument.pop(k, None)
            initial_notes_by_instrument.pop(k, None)
        
        # Build transition matrices for each instrument
        for instr_name, transitions in transitions_by_instrument.items():

            current_notes, next_notes = zip(*transitions)

            current_notes_series = pd.Series(current_notes, name='current')
            next_notes_series = pd.Series(next_notes, name='next')

            counts = pd.crosstab(current_notes_series, next_notes_series)

            all_notes = sorted(list(set(current_notes) | set(next_notes)))
            squared_counts = counts.reindex(index=all_notes, columns=all_notes, fill_value=0)

            # Apply Laplace smoothing
            if laplace_smoothing > 0:
                squared_counts += laplace_smoothing
            
            # Normalize rows to get probabilities
            squared_counts = squared_counts.div(squared_counts.sum(axis=1), axis=0)

            self._transition_matrices[instr_name] = squared_counts
        
        # Build starting probabilities for each instrument
        for instr_name, initial_notes in initial_notes_by_instrument.items():
            initial_notes_series = pd.Series(initial_notes, name='initial').value_counts()
            initial_counts = initial_notes_series.reindex(self._transition_matrices[instr_name].index, fill_value=0)

            self._starting_probabilities[instr_name] = initial_counts / initial_counts.sum()

    def train_models(self) -> None:
        """
        Train the Markov Chain models using the extracted parameters from analyze_data().
        :return: None
        """
        pass