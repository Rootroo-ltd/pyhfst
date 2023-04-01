from enum import Enum
from .common import *


class FlagDiacriticOperator(Enum):
    """
    Enum representing flag diacritic operators.
    """
    P = 0
    N = 1
    R = 2
    D = 3
    C = 4
    U = 5


class FlagDiacriticOperation:
    """
    Class representing a flag diacritic operation.
    """

    def __init__(self, operation: Optional[FlagDiacriticOperator] = None, feat: Optional[int] = None, val: Optional[int] = None):
        """
        Initializes the FlagDiacriticOperation instance.

        :param operation: The flag diacritic operator. Defaults to None.
        :param feat: The feature index. Defaults to None.
        :param val: The value of the feature. Defaults to None.

        """
        if operation is not None:
            self.op = operation
            self.feature = feat
            self.value = val
        else:
            self.op = FlagDiacriticOperator.P
            self.feature = NO_SYMBOL_NUMBER
            self.value = 0

    def is_flag(self) -> bool:
        """
        Checks if the operation is a flag diacritic operation.

        :return: True if the operation is a flag diacritic operation, False otherwise.
        """
        return self.feature != NO_SYMBOL_NUMBER
