import struct
import io
from .byte_array import ByteArray

class TransducerHeader:
    def __init__(self, file):
        # Taken from https://github.com/hfst/hfst-optimized-lookup/blob/938edf4075ab1e3a08017750d80d32e903cf5376/hfst-optimized-lookup-python/hfst_lookup/shared.py
        
        self.intact = True
        bytes = file.read(5) # "HFST\0"
        if self.begins_hfst3_header(bytes):
            self.hfst3 = True
            # just ignore any hfst3 header
            remaining = struct.unpack_from("<H", file.read(3), 0)[0]
            self.handle_hfst3_header(file, remaining)
            bytes = file.read(56) # 2 unsigned shorts, 4 unsigned ints and 9 uint-bools
        else:
            bytes = bytes + file.read(56 - 5)
        self.number_of_input_symbols             = struct.unpack_from("<H", bytes, 0)[0]
        self.number_of_symbols                   = struct.unpack_from("<H", bytes, 2)[0]
        self.size_of_transition_index_table      = struct.unpack_from("<I", bytes, 4)[0]
        self.size_of_transition_target_table     = struct.unpack_from("<I", bytes, 8)[0]
        self.number_of_states                    = struct.unpack_from("<I", bytes, 12)[0]
        self.number_of_transitions               = struct.unpack_from("<I", bytes, 16)[0]
        self.weighted                            = struct.unpack_from("<I", bytes, 20)[0] != 0
        self.deterministic                       = struct.unpack_from("<I", bytes, 24)[0] != 0
        self.input_deterministic                 = struct.unpack_from("<I", bytes, 28)[0] != 0
        self.minimized                           = struct.unpack_from("<I", bytes, 32)[0] != 0
        self.cyclic                              = struct.unpack_from("<I", bytes, 36)[0] != 0
        self.has_epsilon_epsilon_transitions     = struct.unpack_from("<I", bytes, 40)[0] != 0
        self.has_input_epsilon_transitions       = struct.unpack_from("<I", bytes, 44)[0] != 0
        self.has_input_epsilon_cycles            = struct.unpack_from("<I", bytes, 48)[0] != 0
        self.has_unweighted_input_epsilon_cycles = struct.unpack_from("<I", bytes, 52)[0] != 0

    def begins_hfst3_header(self, bytes):
        return len(bytes) >= 5 and bytes == b"HFST\x00"
    

    def handle_hfst3_header(self, file, remaining):
        chars = struct.unpack_from("<" + str(remaining) + "c",
                                   file.read(remaining), 0)

    def get_input_symbol_count(self):
        return self.number_of_input_symbols

    def get_symbol_count(self):
        return self.number_of_symbols

    def get_index_table_size(self):
        return self.size_of_transition_index_table

    def get_target_table_size(self):
        return self.size_of_transition_target_table

    def is_weighted(self):
        return self.weighted

    def has_hfst3_header(self):
        return self.hfst3

    def is_intact(self):
        return self.intact
