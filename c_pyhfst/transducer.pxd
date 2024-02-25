# cython: language_level=3
from .common cimport *
from .transducer_header cimport TransducerHeader
from .transducer_alphabet cimport TransducerAlphabet


cdef class Transducer:
    cdef public TransducerHeader header
    cdef public TransducerAlphabet alphabet
    cdef public bint is_weighted
    cdef public dict operations
    cdef public dict symbol_map
    cdef public IndexTable index_table
    cdef public TransitionTable transition_table
    cpdef void construct_symbol_map(self)