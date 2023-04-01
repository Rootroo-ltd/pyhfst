import struct
from typing import Optional


class ByteArray:
    """
    A simple class for handling byte arrays with various read operations.
    """

    def __init__(self, s: Optional[int] = None, another: Optional['ByteArray'] = None):
        if another is not None:
            s = max(s.get_size(), another.get_size())
            self.bytes = bytearray(another.get_bytes())
        else:
            self.bytes = bytearray(s)
        self.size: int = s
        self.index: int = 0

    def get_size(self) -> int:
        """
        Returns the size of the byte array.

        :return: The size of the byte array.
        """
        return self.size

    def get(self, i: int) -> int:
        """
        Returns the byte at the given index.

        :param i: The index of the byte to retrieve.
        :return: The byte at the specified index.
        """
        return self.bytes[i]

    def get_bytes(self) -> bytearray:
        """
        Returns the byte array.

        :return: The byte array.
        """
        return self.bytes

    def get_ubyte(self) -> int:
        """
        Returns an unsigned byte from the byte array and advances the index.

        :return: An unsigned byte.
        """
        result = self.bytes[self.index]
        self.index += 1
        return result

    def get_ushort(self) -> int:
        """
        Returns an unsigned short from the byte array and advances the index.

        :return: An unsigned short.
        """
        result = struct.unpack_from("<H", self.bytes, self.index)[0]
        self.index += 2
        return result

    def get_uint(self) -> int:
        """
        Returns an unsigned integer from the byte array and advances the index.

        :return: An unsigned integer.
        """
        result = struct.unpack_from("<I", self.bytes, self.index)[0]
        self.index += 4
        return result

    def get_bool(self) -> bool:
        """
        Returns a boolean value from the byte array and advances the index.

        :return: A boolean value.
        """
        return self.get_uint() != 0

    def get_float(self) -> float:
        """
        Returns a floating-point number from the byte array and advances the index.

        :return: A floating-point number.
        """
        result = struct.unpack_from("<f", self.bytes, self.index)[0]
        self.index += 4
        return result
