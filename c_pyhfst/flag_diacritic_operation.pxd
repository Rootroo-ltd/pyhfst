# flag_diacritic_operation.pxd

from .common cimport *
from .flag_diacritic_operator cimport FlagDiacriticOperator

cdef class FlagDiacriticOperation:
    cdef FlagDiacriticOperator op
    cdef int feature
    cdef int value
    cpdef bint is_flag(self)
