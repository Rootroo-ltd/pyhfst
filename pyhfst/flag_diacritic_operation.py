from enum import Enum
from .common import *

class FlagDiacriticOperator(Enum):
    P = 0
    N = 1
    R = 2
    D = 3
    C = 4
    U = 5

class FlagDiacriticOperation:
    def __init__(self, operation=None, feat=None, val=None):
        if operation is not None:
            self.op = operation
            self.feature = feat
            self.value = val
        else:
            self.op = FlagDiacriticOperator.P
            self.feature = NO_SYMBOL_NUMBER
            self.value = 0

    def is_flag(self):
        return self.feature != NO_SYMBOL_NUMBER