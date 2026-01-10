import os
import music21
import numpy as np

class MusicalMarkovChain:
    def __init__(self, input_path: str = 'MIDI_files'):
        self.input_path = input_path
        self.note_T_matrix = None
        self.note_to_index = None
        self.index_to_note = None
        self.scores = self.__parse_input__(input_path)
        self.all_instruments = self.__get_all_instruments__()

    def generate_music(self):
        pass

    def __parse_input__(self, input_path: str = 'MIDI_files') -> list[music21.stream.Score]:
        """
        Parse MIDI files from the given directory and partition them by instruments.
        :param input_path: Path to the directory containing MIDI files.
        :return: List of partitioned music21 Score objects.
        """

        path = os.fsencode(input_path)
        scores = []

        for file in os.listdir(path):
            filename = os.fsdecode(file)
            if filename.endswith('.mid') or filename.endswith('.midi'):
                midi_path = os.path.join(input_path, filename)
                score = music21.converter.parse(midi_path)
                score = music21.instrument.partitionByInstrument(score)
                scores.append(score)
        return scores
    
    def __get_all_instruments__(self) -> list[str]:
        """
        Get a list of all unique instruments from the parsed scores.
        :return: List of instrument names.
        """
        instruments = set()

        for score in self.scores:
            for part in score.parts:
                instr = part.getInstrument()
                instruments.add(instr.instrumentName)

        return list(instruments)