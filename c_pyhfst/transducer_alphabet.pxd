# cython: language_level=3
cdef class TransducerAlphabet:
    cdef public list keyTable
    cdef public dict operations
    cdef public dict feature_bucket
    cdef public dict value_bucket
    cdef public int features
    cdef public int values