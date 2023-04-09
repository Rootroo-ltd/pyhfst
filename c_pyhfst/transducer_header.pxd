cdef class TransducerHeader:
    cdef int number_of_input_symbols
    cdef int number_of_symbols
    cdef int size_of_transition_index_table
    cdef int size_of_transition_target_table
    cdef int number_of_states
    cdef int number_of_transitions
    cdef bint weighted
    cdef bint deterministic
    cdef bint input_deterministic
    cdef bint minimized
    cdef bint cyclic
    cdef bint has_epsilon_epsilon_transitions
    cdef bint has_input_epsilon_transitions
    cdef bint has_input_epsilon_cycles
    cdef bint has_unweighted_input_epsilon_cycles
    cdef bint hfst3
    
    cpdef bint begins_hfst3_header(self, bytes b)
    cpdef public int get_input_symbol_count(self)
    cpdef public int get_symbol_count(self)
    cpdef public int get_index_table_size(self)
    cpdef public int get_target_table_size(self)
    cpdef public bint is_weighted(self)
    cpdef bint has_hfst3_header(self)
