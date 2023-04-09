# cython: language_level=3
from libc.stdint cimport uint8_t, uint16_t, uint32_t
import struct

cdef class ByteArray:
    """
    A simple class for handling byte arrays with various read operations.
    """
    def __init__(self, int s=0, ByteArray another=None):
        if another is not None:
            s = max(s, another.get_size())
            self.bytes = bytearray(another.get_bytes())
        else:
            self.bytes = bytearray(s)
        self.size = s
        self.index = 0

    cpdef public int get_size(self):
        """
        Returns the size of the byte array.

        :return: The size of the byte array.
        """
        return self.size

    cpdef public bytes get(self, int i):
        """
        Returns the byte at the given index.

        :param i: The index of the byte to retrieve.
        :return: The byte at the specified index.
        """
        return self.bytes[i]

    cpdef public bytearray get_bytes(self):
        """
        Returns the byte array.

        :return: The byte array.
        """
        return self.bytes

    cpdef public uint8_t get_ubyte(self):
        """
        Returns an unsigned byte from the byte array and advances the index.

        :return: An unsigned byte.
        """
        cdef uint8_t result = self.bytes[self.index]
        self.index += 1
        return result

    cpdef public uint16_t get_ushort(self):
        """
        Returns an unsigned short from the byte array and advances the index.

        :return: An unsigned short.
        """
        cdef uint16_t result = struct.unpack_from("<H", self.bytes, self.index)[0]
        self.index += 2
        return result

    cpdef public uint32_t get_uint(self):
        """
        Returns an unsigned integer from the byte array and advances the index.

        :return: An unsigned integer.
        """
        cdef uint32_t result = struct.unpack_from("<I", self.bytes, self.index)[0]
        self.index += 4
        return result

    cpdef public bint get_bool(self):
        """
        Returns a boolean value from the byte array and advances the index.

        :return: A boolean value.
        """
        return self.get_uint() != 0

    cpdef public float get_float(self):
        """
        Returns a floating-point number from the byte array and advances the index.

        :return: A floating-point number.
        """
        cdef float result = struct.unpack_from("<f", self.bytes, self.index)[0]
        self.index += 4
        return result
