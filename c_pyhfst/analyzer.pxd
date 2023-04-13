# cython: language_level=3
from .common cimport *
from .flag_diacritic_operation cimport FlagDiacriticOperation
from .transducer import Transducer
import cython


cdef class Analyzer:
    cdef Transducer transducer
    cdef str input_str
    cdef State state


    cpdef cython.longlong pivot(self, cython.longlong i)
    cpdef void try_epsilon_indices(self, cython.longlong index)
    cpdef void try_epsilon_transitions(self, cython.longlong index)
    cpdef void find_index(self, cython.longlong index)
    cpdef void handle_epsilon_transition(self, cython.longlong index)
    cpdef void find_transitions(self, cython.longlong index)
    cpdef void get_analyses(self, cython.longlong idx)
    cpdef void update_output_string(self, cython.longlong output_symbol)
    cpdef void handle_end_of_input_string(self, cython.longlong index, bint is_transition)
    cpdef void reset_output_pointer(self)
    cpdef tuple get_final_and_weight(self, cython.longlong index, bint is_transition)
    cpdef void update_and_note_analysis(self, float weight)
    cpdef list get_symbols(self)
    cpdef void note_analysis(self)
    cpdef list get_alphabet(self)
    cpdef public list analyze(self)
    cpdef bint push_state(self, FlagDiacriticOperation flag)