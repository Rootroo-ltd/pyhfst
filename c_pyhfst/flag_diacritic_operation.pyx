# cython: language_level=3
from .common cimport *
from .flag_diacritic_operator cimport FlagDiacriticOperator

cdef class FlagDiacriticOperation:
    """
    Class representing a flag diacritic operation.
    """
    def __init__(self, FlagDiacriticOperator operation, int feat, int val=0):
        """
        Initializes the FlagDiacriticOperation instance.

        :param operation: The flag diacritic operator. Defaults to None.
        :param feat: The feature index. Defaults to None.
        :param val: The value of the feature. Defaults to None.

        """
        self.op = operation if operation else FlagDiacriticOperator.P
        self.feature = feat
        self.value = val

    cpdef bint is_flag(self):
        """
        Checks if the operation is a flag diacritic operation.

        :return: True if the operation is a flag diacritic operation, False otherwise.
        """
        return self.feature != NO_SYMBOL_NUMBER
