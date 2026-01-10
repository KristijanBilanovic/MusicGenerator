import os
import music21

class MusicDataTrainer:
    def __init__(self, data_path: str = 'MIDI_files'):
        self.data_path = data_path
        self.matrices = []
        self.scores = self._load_data()
        self.instrument_mapping = self._get_all_instruments()
        

    def _load_data(self) -> list[music21.stream.Score]:
        """
        Parse MIDI files from the given directory and partition them by instruments.
        :param input_path: Path to the directory containing MIDI files.
        :return: List of partitioned music21 Score objects.
        """
        scores = []

        for root, dirs, files in os.walk(self.data_path):
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

        for score in self.scores:
            for part in score.parts:
                instr = part.getInstrument()
                if instr.instrumentName not in instrument_mapping:
                    instrument_mapping[instr.instrumentName] = index
                    index += 1

        return instrument_mapping

    def analyze_data(self) -> None:
        """
        Creates parameters needed for Markov Chain probabilistic model - transition matrices and starting probabilities.
        The models are NOT trained yet after running this method. For training, call the train_models() method.
        :return: None
        """
        pass

    def train_models(self) -> None:
        """
        Train the Markov Chain models using the extracted parameters from analyze_data().
        :return: None
        """
        pass