# cython: language_level=3
from .byte_array cimport ByteArray
import io
import struct

cdef class TransducerHeader:
    """
    A class representing the header of the transducer.
    """

    def __init__(self, input_bytes: io.BytesIO):
        read_bytes: bytes = input_bytes.read(5)  # "HFST\0"
        if self.begins_hfst3_header(read_bytes):
            # just ignore any hfst3 header
            self.hfst3: bool = True
            remaining = struct.unpack_from("<H", input_bytes.read(3), 0)[
                0]  # get remaining
            struct.unpack_from(f"<{remaining}c", input_bytes.read(
                remaining), 0)  # skip remaining
            # 2 unsigned shorts, 4 unsigned ints and 9 uint-bools
            read_bytes = input_bytes.read(56)
        else:
            read_bytes = read_bytes + input_bytes.read(56 - 5)

        cdef ByteArray bytes_array = ByteArray(len(read_bytes))
        bytes_array.bytes = bytearray(read_bytes)

        self.number_of_input_symbols = bytes_array.get_ushort()
        self.number_of_symbols = bytes_array.get_ushort()
        self.size_of_transition_index_table = bytes_array.get_uint()
        self.size_of_transition_target_table = bytes_array.get_uint()
        self.number_of_states = bytes_array.get_uint()
        self.number_of_transitions = bytes_array.get_uint()
        self.weighted = bytes_array.get_bool()
        self.deterministic = bytes_array.get_bool()
        self.input_deterministic = bytes_array.get_bool()
        self.minimized = bytes_array.get_bool()
        self.cyclic = bytes_array.get_bool()
        self.has_epsilon_epsilon_transitions = bytes_array.get_bool()
        self.has_input_epsilon_transitions = bytes_array.get_bool()
        self.has_input_epsilon_cycles = bytes_array.get_bool()
        self.has_unweighted_input_epsilon_cycles = bytes_array.get_bool()

    cpdef bint begins_hfst3_header(self, bytes b):
        """
        Checks if the given bytes begin with the HFST3 header.

        :param bytes: The bytes to check.
        :return: True if the bytes begin with the HFST3 header, False otherwise.
        """
        return len(b) >= 5 and b == b"HFST\x00"

    cpdef public int get_input_symbol_count(self):
        """
        Returns the number of input symbols.

        :return: The number of input symbols.
        """
        return self.number_of_input_symbols

    cpdef public int get_symbol_count(self):
        """
        Returns the number of symbols.

        :return: The number of symbols.
        """
        return self.number_of_symbols

    cpdef public int get_index_table_size(self):
        """
        Returns the size of the transition index table.
        :return: The size of the transition index table.
        """
        return self.size_of_transition_index_table

    cpdef public int get_target_table_size(self):
        """
        Returns the size of the transition target table.

        :return: The size of the transition target table.
        """
        return self.size_of_transition_target_table

    cpdef public bint is_weighted(self):
        """
        Checks if the transducer is weighted.

        :return: True if the transducer is weighted, False otherwise.
        """
        return self.weighted

    cpdef bint has_hfst3_header(self):
        """
        Checks if the transducer has an HFST3 header.

        :return: True if the transducer has an HFST3 header, False otherwise.
        """
        return self.hfst3
