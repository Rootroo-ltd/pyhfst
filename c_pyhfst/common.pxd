# cython: language_level=3
from libc.stdint cimport uint32_t, uint16_t
from cpython cimport dict, array
import cython
from .transducer cimport Transducer

cdef extern from "constants.h":   
    cdef cython.longlong TRANSITION_TARGET_TABLE_START = 2147483648
    cdef cython.longlong INFINITE_WEIGHT = 4294967295
    cdef cython.longlong NO_SYMBOL_NUMBER = 65535
    cdef cython.longlong NO_TABLE_INDEX = 4294967295

cdef class IndexTable:
    cdef array.array ti_input_symbols
    cdef array.array ti_targets
    cdef cython.longlong _size

    cpdef uint16_t get_input(self, int i)
    cpdef uint32_t get_target(self, int i)
    cpdef bint is_final(self, int i)
    cpdef float get_final_weight(self, int i)

cdef class TransitionTable:
    cdef array.array ti_input_symbols
    cdef array.array ti_output_symbols
    cdef array.array ti_targets
    cdef array.array ti_weights
    cdef bint is_weighted
    cdef cython.longlong _size

    cpdef uint16_t get_input(self, int pos)
    cpdef uint16_t get_output(self, int pos)
    cpdef uint32_t get_target(self, int pos)
    cpdef float get_weight(self, int pos)
    cpdef bint is_final(self, int pos)
    cpdef int size(self)

cdef class State:
    cdef public Transducer parent
    cdef public list state_stack
    cdef public list output_string
    cdef public list input_string
    cdef public int output_pointer
    cdef public int input_pointer
    cdef public float current_weight
    cdef public list display_vector

    cdef list find_key(self, str index_string)
    
cdef class Result:
    cdef list symbols
    cdef float weight

    cpdef list get_symbols(self)
    cpdef float get_weight(self)
