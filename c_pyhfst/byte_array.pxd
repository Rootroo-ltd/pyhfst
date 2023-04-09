# bytearray.pxd

from libc.stdint cimport uint8_t, uint16_t, uint32_t

cdef class ByteArray:

    cdef bytearray bytes
    cdef int size
    cdef int index

    cpdef public int get_size(self)
    cpdef public bytes get(self, int i)
    cpdef public bytearray get_bytes(self)
    cpdef public uint8_t get_ubyte(self)
    cpdef public uint16_t get_ushort(self)
    cpdef public uint32_t get_uint(self)
    cpdef public bint get_bool(self)
    cpdef public float get_float(self)
