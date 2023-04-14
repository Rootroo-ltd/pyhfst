from typing import Union, List, Tuple
from pathlib import Path
from io import BufferedReader


try:
    from c_pyhfst.transducer import Transducer
    from c_pyhfst.transducer_header import TransducerHeader
    from c_pyhfst.transducer_alphabet import TransducerAlphabet
    from c_pyhfst.analyzer import Analyzer
except:
    from .transducer import Transducer
    from .transducer_header import TransducerHeader
    from .transducer_alphabet import TransducerAlphabet
    from .analyzer import Analyzer

def get_transducer(transducer_path: Union[str, Path]) -> Transducer:
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


class HfstInputStream(object):
    def __init__(self, path: Union[str, Path], cache=True) -> None:
        """
        Initialize an HfstInputStream object.

        :param path: The path to the transducer file.
        :param cache: Whether to cache the results.
        """
        self.path = path
        self.cache = cache

    def read(self) -> 'Hfst':
        """
        Read the transducer file and return an Hfst object.

        :return: An Hfst object initialized with the transducer read from the file.
        """
        tr = get_transducer(self.path)
        return Hfst(tr, cache=self.cache)


class Hfst(object):
    def __init__(self, tr: Transducer, cache=True) -> None:
        """
        Initialize an Hfst object with a given transducer.

        :param tr: The transducer object.
        :param cache: Whether to cache the results.
        """
        self.tr = tr
        self.cache = cache
        self.mem = {}


    def lookup(self, string: str) -> List[Tuple[str, float]]:
        """
        Perform lookup on the input string and return the analyses.

        :param string: The input string to analyze.
        :return: A list of tuples, where each sublist contains the string representation of the result and its weight.
        """
        if self.cache:
            if string not in self.mem:
                self.mem[string] = Analyzer(self.tr, string).analyze()
            result = self.mem[string]
        else:
            result = Analyzer(self.tr, string).analyze()
        return [["".join(_r.get_symbols()), _r.get_weight()] for _r in result]
