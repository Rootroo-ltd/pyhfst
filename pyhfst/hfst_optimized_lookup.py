import sys
from io import BufferedReader, StringIO
from collections import namedtuple
from .transducer import Transducer
from .transducer_header import TransducerHeader
from .transducer_alphabet import TransducerAlphabet
from .transducer import Transducer

class HfstOptimizedLookup:
    @staticmethod
    def run_transducer(transducer: Transducer):
        stdin = BufferedReader(StringIO(sys.stdin.read()))
        while True:
            try:
                line = stdin.readline()
                if not line:
                    break
                str_input = line.strip()
            except Exception as e:
                break

            analyses = transducer.analyze(str_input)
            for analysis in analyses:
                print(f"{str_input}\t{analysis}")
            if not analyses:
                print(f"{str_input}\t+?")
            print()

    def main(self, argv):
        if len(argv) != 1:
            sys.stderr.write("Usage: python hfst_optimized_lookup.py FILE\n")
            sys.exit(1)

        transducer_file = None
        try:
            transducer_file = open(argv[0], "rb")
        except FileNotFoundError:
            sys.stderr.write(f"File not found: couldn't read transducer file {argv[0]}.\n")
            sys.exit(1)

        char_stream= BufferedReader(transducer_file)
        transducer_header = TransducerHeader(char_stream)
        transducer_alphabet = TransducerAlphabet(char_stream, transducer_header.get_symbol_count())
        if transducer_header.is_weighted():
            transducer = Transducer(char_stream, transducer_header, transducer_alphabet, is_weighted=True)
            # self.run_transducer(transducer)
        else:
            transducer = Transducer(char_stream, transducer_header, transducer_alphabet, is_weighted=False)
            # self.run_transducer(transducer)
        return transducer
