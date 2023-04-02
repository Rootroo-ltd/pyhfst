import io
from typing import List, Dict
from .flag_diacritic_operation import FlagDiacriticOperator


class FlagDiacriticOperation:

    def __init__(self, operation, feat, val):
        self.op = operation
        self.feature = feat
        self.value = val


class TransducerAlphabet:
    def __init__(self, charstream: io.BytesIO, number_of_symbols: int) -> None:
        """
        Initializes the TransducerAlphabet instance.

        :param charstream: A byte stream containing the alphabet data.
        :param number_of_symbols: The number of symbols in the alphabet.
        """
        self.keyTable: List[str] = []
        self.operations: Dict[int, FlagDiacriticOperation] = {}
        feature_bucket: Dict[str, int] = {}
        value_bucket: Dict[str, int] = {}
        self.features = 0
        values = 1
        value_bucket[""] = 0  # neutral value

        chars = bytearray()
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
                and ustring[0] == "@"
                and ustring[-1] == "@"
                and ustring[2] == "."
            ):  # flag diacritic identified
                op: FlagDiacriticOperator
                parts = ustring[1:-1].split(".")
                # Not a flag diacritic after all, ignore it
                if len(parts) < 2:
                    self.keyTable.append("")
                    continue
                ops, feats, *remainder = parts
                vals = remainder[0] if remainder else ""

                op = FlagDiacriticOperator[ops]

                if op is None:  # Not a valid operator, ignore the operation
                    self.keyTable.append("")
                    continue

                if vals not in value_bucket:
                    value_bucket[vals] = values
                    values += 1
                if feats not in feature_bucket:
                    feature_bucket[feats] = self.features
                    self.features += 1
                self.operations[len(self.keyTable)] = FlagDiacriticOperation(
                    op, feature_bucket[feats], value_bucket[vals]
                )
                self.keyTable.append("")
                continue
            self.keyTable.append(ustring)
        self.keyTable[0] = ""  # epsilon is zero
