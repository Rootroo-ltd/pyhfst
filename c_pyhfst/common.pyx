# cython: language_level=3
from libc.stdint cimport uint32_t, uint16_t, int32_t
import io
from .byte_array cimport ByteArray
cimport cython

cdef class IndexTable:
    def __init__(self, input_stream: io.BytesIO, cython.longlong indices_count):
        b = ByteArray(indices_count * 6)
        input_stream.readinto(b.bytes)

        self._size = indices_count
        self.ti_input_symbols = array.array('H', [])
        array.resize(self.ti_input_symbols, self._size)

        self.ti_targets = array.array('I', [])
        array.resize(self.ti_targets, self._size)

        for i in range(indices_count):
            self.ti_input_symbols[i] = b.get_ushort()
            self.ti_targets[i] = b.get_uint()

    cpdef uint16_t get_input(self, int i):
        i = i % self._size
        return self.ti_input_symbols[i]

    cpdef uint32_t get_target(self, int i):
        i = i % self._size
        return self.ti_targets[i]

    cpdef bint is_final(self, int i):
        i = i % self._size
        return (self.ti_input_symbols[i] == NO_SYMBOL_NUMBER and self.ti_targets[i] != NO_TABLE_INDEX)

    cpdef float get_final_weight(self, int i):
        i = i % self._size
        return float(self.ti_targets[i])


cdef class TransitionTable:
    def __init__(self, input_stream: io.BytesIO, cython.longlong transition_count, bint is_weighted=True):
        b = ByteArray(transition_count * 12)
        input_stream.readinto(b.bytes)

        self._size = transition_count

        self.is_weighted = is_weighted

        self.ti_input_symbols = array.array('H', [])
        array.resize(self.ti_input_symbols, self._size)

        self.ti_output_symbols = array.array('H', [])
        array.resize(self.ti_output_symbols, self._size)

        self.ti_targets = array.array('I', [])
        array.resize(self.ti_targets, self._size)

        self.ti_weights = array.array('f', [])
        array.resize(self.ti_weights, self._size)

        for i in range(transition_count):
            self.ti_input_symbols[i] = b.get_ushort()
            self.ti_output_symbols[i] = b.get_ushort()
            self.ti_targets[i] = b.get_uint()
            if self.is_weighted:
                self.ti_weights[i] = b.get_float()

    cpdef uint16_t get_input(self, int pos):
        pos = pos % self._size
        return self.ti_input_symbols[pos]

    cpdef uint16_t get_output(self, int pos):
        pos = pos % self._size
        return self.ti_output_symbols[pos]

    cpdef uint32_t get_target(self, int pos):
        pos = pos % self._size
        return self.ti_targets[pos]

    cpdef float get_weight(self, int pos):
        pos = pos % self._size
        if not self.is_weighted:
            raise Exception("Getting weights of unweighted FST.")
        return self.ti_weights[pos]

    cpdef bint is_final(self, int pos):
        pos = pos % self._size
        return (self.ti_input_symbols[pos] == NO_SYMBOL_NUMBER and
                self.ti_output_symbols[pos] == NO_SYMBOL_NUMBER and
                self.ti_targets[pos] == 1)

    cpdef int size(self):
        return self._size

cdef class State:
    def __init__(self, str input, parent):
        self.parent = parent
        self.state_stack = []
        neutral = [0] * parent.alphabet.features
        self.state_stack.append(neutral)
        self.output_string = [NO_SYMBOL_NUMBER] * 1000
        self.input_string = self.find_key(input)
        self.output_pointer = 0
        self.input_pointer = 0
        self.current_weight = 0.0
        self.display_vector = []

    cdef list find_key(self, str index_string):
        output = list()

        _pos = 0
        while _pos < len(index_string):
            for _length in range(1, len(index_string[_pos:]) + 1):
                _x = index_string[_pos :_pos + _length]
                try:
                    output.append(self.parent.symbol_map[_x])
                except:
                    break
            _pos += 1

        output.append(NO_SYMBOL_NUMBER)

        return output

cdef class Result:
    def __init__(self, list symbols, float weight):
        self.symbols = symbols
        self.weight = weight
    cpdef list get_symbols(self):
        return self.symbols

    cpdef float get_weight(self):
        return self.weight

    def __str__(self):
        return ''.join(self.symbols) + ": " + str(self.weight)
