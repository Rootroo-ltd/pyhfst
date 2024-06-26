from .common import *
from .transducer_header import TransducerHeader
from .transducer_alphabet import TransducerAlphabet


class Transducer:
    """
    A class representing a finite state transducer for morphological analysis.
    """

    def __init__(
        self, file, h: TransducerHeader, a: TransducerAlphabet, is_weighted: bool = True
    ) -> None:
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

        self.symbol_map = {}
        self.construct_symbol_map()

        self.index_table = IndexTable(file, h.get_index_table_size())
        self.transition_table = TransitionTable(
            file, h.get_target_table_size(), is_weighted=self.is_weighted
        )

    def construct_symbol_map(self):
        for i in range(self.header.get_input_symbol_count()):
            _w = self.alphabet.keyTable[i]
            if len(_w) <= 1:
                self.symbol_map[_w] = {None: i}
            else:
                if _w[0] not in self.symbol_map:
                    self.symbol_map[_w[0]] = {}
                _o = self.symbol_map[_w[0]]
                for j in range(1, len(_w)):
                    _c = _w[j]
                    if _c not in _o:
                        _o[_c] = {}
                    _o = _o[_c]
                if None in _o:
                    raise ValueError("Duplicate symbol in symbol map")
                _o[None] = i
