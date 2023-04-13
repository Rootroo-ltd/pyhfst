from typing import Union, List
from pathlib import Path
from io import BufferedReader
from .transducer_header cimport TransducerHeader
from .transducer_alphabet cimport TransducerAlphabet
from .transducer cimport Transducer as Transducer
from .analyzer import Analyzer

cpdef Transducer get_transducer(transducer_path: Union[str, Path]):
    """
    Creates a Transducer instance from the given transducer file path.

    :param transducer_path: The path to the transducer file.
    :return: A Transducer instance.
    """
    with open(transducer_path, "rb") as transducer_file:
        char_stream = BufferedReader(transducer_file)
        transducer_header = TransducerHeader(char_stream)
        transducer_alphabet = TransducerAlphabet(
            char_stream, transducer_header.get_symbol_count()
        )
        return Transducer(char_stream, transducer_header, transducer_alphabet, is_weighted=transducer_header.is_weighted())