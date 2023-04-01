import struct

class ByteArray:
    def __init__(self, s=None, another=None):
        if another is not None:
            s = max(s.get_size(), another.get_size())
            self.bytes = bytearray(another.get_bytes())
        else:
            self.bytes = bytearray(s)
        self.size = s
        self.index = 0

    def get_size(self):
        return self.size

    def get(self, i):
        return self.bytes[i]

    def get_bytes(self):
        return self.bytes

    def get_ubyte(self):
        result = self.bytes[self.index]
        self.index += 1
        return result

    def get_ushort(self):
        result = struct.unpack_from("<H", self.bytes, self.index)[0]
        self.index += 2
        return result

    def get_uint(self):
        result = struct.unpack_from("<I", self.bytes, self.index)[0]
        self.index += 4
        return result

    def get_bool(self):
        return self.get_uint() != 0

    def get_float(self):
        result = struct.unpack_from("<f", self.bytes, self.index)[0]
        self.index += 4
        return result
