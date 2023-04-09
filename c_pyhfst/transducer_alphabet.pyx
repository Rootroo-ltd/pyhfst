# cython: language_level=3
from .flag_diacritic_operator cimport FlagDiacriticOperator
import io

cdef class TransducerAlphabet:
    def __init__(self, charstream: io.BytesIO, int number_of_symbols):
        """
        Initializes the TransducerAlphabet instance.

        :param filename: The file containing the alphabet data.
        :param number_of_symbols: The number of symbols in the alphabet.
        """
        self.keyTable = []
        self.operations = {}
        feature_bucket = {}
        value_bucket = {}
        self.features = 0
        self.values = 1
        value_bucket[""] = 0  # neutral value
        cdef str ops_index = "PNRDCU"

        cdef bytearray chars = bytearray()
        cdef str ustring
        cdef int charindex = 0
        cdef FlagDiacriticOperator op
        cdef str vals, feats, ops

        for _ in range(number_of_symbols):
            charindex = 0
            if len(chars) == charindex:
                chars.append(charstream.read(1)[0])
            else:
                chars[charindex] = charstream.read(1)[0]
            while chars[charindex] != 0:
                charindex += 1
                if len(chars) == charindex:
                    chars.append(charstream.read(1)[0])
                else:
                    chars[charindex] = charstream.read(1)[0]
            ustring = chars[:charindex].decode("utf-8")

            if (
                len(ustring) > 5
                and ustring[0] == ord("@")
                and ustring[-1] == ord("@")
                and ustring[2] == ord(".")
            ):  # flag diacritic identified
                parts = ustring[1:-1].split(".")
                if len(parts) < 2:
                    self.keyTable.append("")
                    continue
                ops, feats, *remainder = parts
                vals = remainder[0] if remainder else ""
                
                op = ops_index.index(ops)
                

                if op is None:  # Not a valid operator, ignore the operation
                    self.keyTable.append("")
                    continue

                if feats not in feature_bucket:
                    feature_bucket[feats] = self.features
                    self.features += 1
                if vals not in value_bucket:
                    value_bucket[vals] = self.values
                    self.values += 1
                self.operations[len(self.keyTable)] = FlagDiacriticOperation(
                    op, feature_bucket[feats], value_bucket[vals]
                )
                self.keyTable.append("")
                continue
            self.keyTable.append(ustring)
        self.keyTable[0] = ""  # epsilon is zero
