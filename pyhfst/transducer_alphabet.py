import io
from typing import List
from .flag_diacritic_operation  import FlagDiacriticOperator

class FlagDiacriticOperation:
    def __init__(self, operation, feat, val):
        self.op = operation
        self.feature = feat
        self.value = val

class TransducerAlphabet:
    def __init__(self, charstream: io.BytesIO, number_of_symbols: int) -> None:
        self.keyTable: List[str] = []
        self.operations = {}
        feature_bucket = {}
        value_bucket = {}
        self.features = 0
        values = 1
        value_bucket[""] = 0  # neutral value
        i = 0
        chars = bytearray()
        while i < number_of_symbols:
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
                    i += 1
                    continue
                ops = parts[0]
                feats = parts[1]
                if len(parts) == 3:
                    vals = parts[2]
                else:
                    vals = ""
                if ops == "P":
                    op = FlagDiacriticOperator.P
                elif ops == "N":
                    op = FlagDiacriticOperator.N
                elif ops == "R":
                    op = FlagDiacriticOperator.R
                elif ops == "D":
                    op = FlagDiacriticOperator.D
                elif ops == "C":
                    op = FlagDiacriticOperator.C
                elif ops == "U":
                    op = FlagDiacriticOperator.U
                else:  # Not a valid operator, ignore the operation
                    self.keyTable.append("")
                    i += 1
                    continue
                if vals not in value_bucket:
                    value_bucket[vals] = values
                    values += 1
                if feats not in feature_bucket:
                    feature_bucket[feats] = self.features
                    self.features += 1
                self.operations[i] = FlagDiacriticOperation(
                    op, feature_bucket[feats], value_bucket[vals]
                )
                self.keyTable.append("")
                i += 1
                continue
            self.keyTable.append(ustring)
            i += 1
        self.keyTable[0] = ""  # epsilon is zero
