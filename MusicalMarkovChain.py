import os
import music21
import numpy as np
import pandas as pd

class MusicalMarkovChain:
    def __init__(self, transition_matrix: pd.DataFrame, starting_probabilities: pd.Series):
        self._transition_matrix = transition_matrix
        self._starting_probabilities = starting_probabilities
    
    def generate_sequence(self, length: int = 50) -> list:
        """
        Generate a sequence of states based on the Markov Chain model.
        
        :param length: Length of the sequence to generate.
        :type length: int
        :return: Generated sequence of states.
        :rtype: list
        """
        states = self._transition_matrix.index.tolist()
        current_state = np.random.choice(states, p=self._starting_probabilities.values)
        sequence = [current_state]
        
        for _ in range(1, length):
            current_row = self._transition_matrix.loc[current_state]
            next_state = np.random.choice(states, p=current_row.values)
            sequence.append(next_state)
            current_state = next_state
        
        return sequence