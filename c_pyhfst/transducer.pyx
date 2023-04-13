# cython: language_level=3
from .common cimport *
from .transducer_header cimport TransducerHeader
from .transducer_alphabet cimport TransducerAlphabet

cdef class Transducer:
    """
    A class representing a finite state transducer for morphological analysis.
    """

    def __init__(self, file, TransducerHeader h, TransducerAlphabet a, bint is_weighted=True):
        """
        Initializes the Transducer instance.

        :param file: A file containing the transducer data.
        :param h: A TransducerHeader instance representing the header of the transducer.
        :param a: A TransducerAlphabet instance representing the alphabet of the transducer.
        :param is_weighted: A boolean indicating if the transducer is weighted. Defaults to True.
        """
        self.header = h
        self.alphabet = a
        self.is_weighted = is_weighted
        self.operations = self.alphabet.operations
        self.symbol_map = {self.alphabet.keyTable[i]:i for i in range(h.get_input_symbol_count())}
        self.index_table = IndexTable(file, h.get_index_table_size())
        self.transition_table = TransitionTable(
            file, h.get_target_table_size(), is_weighted=self.is_weighted)