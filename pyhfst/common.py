from typing import List
from collections import defaultdict
from .byte_array import ByteArray

# 2^31 or UINT_MAX/2 rounded up
TRANSITION_TARGET_TABLE_START = 2147483648
# this is hopefully the same as static_cast<float>(UINT_MAX) in C++
INFINITE_WEIGHT = float(4294967295)
# USHRT_MAX
NO_SYMBOL_NUMBER = 65535
NO_TABLE_INDEX = 4294967295

class LetterTrie:
    class LetterTrieNode:
        def __init__(self):
            self.symbols = defaultdict()
            self.children = defaultdict()

        def add_string(self, string, symbol_number):
            if len(string) > 1:
                if string[0] not in self.children:
                    self.children[string[0]] = LetterTrie.LetterTrieNode()
                self.children[string[0]].add_string(string[1:], symbol_number)
            elif len(string) == 1:
                self.symbols[string[0]] = symbol_number

        def find_key(self, index_string):
            if index_string.index >= len(index_string.str):
                return NO_SYMBOL_NUMBER
            at_s = index_string.str[index_string.index]
            index_string.index += 1
            child = self.children.get(at_s)
            if child is None:
                symbol = self.symbols.get(at_s)
                if symbol == 0:
                    index_string.index -= 1
                    return NO_SYMBOL_NUMBER
                return symbol
            s = child.find_key(index_string)
            if s == NO_SYMBOL_NUMBER:
                symbol = self.symbols.get(at_s)
                if symbol == 0:
                    index_string.index -= 1
                    return NO_SYMBOL_NUMBER
                return symbol
            return s

    def __init__(self):
        self.root = LetterTrie.LetterTrieNode()

    def add_string(self, string, symbol_number):
        self.root.add_string(string, symbol_number)

    def find_key(self, index_string):
        return self.root.find_key(index_string)
    
class IndexString:
    def __init__(self, s: str):
        self.str = s
        self.index = 0
        
class IndexTable:
    def __init__(self, input_stream, indices_count):
        b = ByteArray(indices_count * 6)
        input_stream.readinto(b.bytes)
        self.ti_input_symbols = [0] * indices_count
        self.ti_targets = [0] * indices_count
        i = 0
        while i < indices_count:
            self.ti_input_symbols[i] = b.get_ushort()
            self.ti_targets[i] = b.get_uint()
            i += 1

    def get_input(self, i):
        return self.ti_input_symbols[i]

    def get_target(self, i):
        return self.ti_targets[i]

    def is_final(self, i):
        return (self.ti_input_symbols[i] == NO_SYMBOL_NUMBER and self.ti_targets[i] != NO_TABLE_INDEX)

    def get_final_weight(self, i):
        return float(self.ti_targets[i])
    
class TransitionTable:
    def __init__(self, input_stream, transition_count, is_weighted=True):
        b = ByteArray(transition_count * 12)
        input_stream.readinto(b.bytes)
        self.is_weighted = is_weighted
        self.ti_input_symbols = [0] * transition_count
        self.ti_output_symbols = [0] * transition_count
        self.ti_targets = [0] * transition_count
        self.ti_weights = [0.0] * transition_count
        i = 0
        while i < transition_count:
            self.ti_input_symbols[i] = b.get_ushort()
            self.ti_output_symbols[i] = b.get_ushort()
            self.ti_targets[i] = b.get_uint()
            if self.is_weighted:
                self.ti_weights[i] = b.get_float()
            i += 1

    def get_input(self, pos):
        return self.ti_input_symbols[pos]

    def get_output(self, pos):
        return self.ti_output_symbols[pos]

    def get_target(self, pos):
        return self.ti_targets[pos]

    def get_weight(self, pos):
        if not self.is_weighted:
            raise Exception("Getting weights of unweighted FST.")
        return self.ti_weights[pos]
    
    def is_final(self, pos):
        return self.ti_input_symbols[pos] == NO_SYMBOL_NUMBER and self.ti_output_symbols[pos] == NO_SYMBOL_NUMBER and self.ti_targets[pos] == 1

    def size(self):
        return len(self.ti_targets)
    
class State:
    def __init__(self, input: str, parent):
        self.parent = parent
        self.state_stack = []
        neutral = [0] * parent.alphabet.features
        self.state_stack.append(neutral)
        self.output_string = [ NO_SYMBOL_NUMBER ] * 1000
        self.input_string = []
        self.output_pointer = 0
        self.input_pointer = 0
        self.current_weight = 0.0
        self.display_vector = []

        input_line = IndexString(input)
        while input_line.index < len(input):
            self.input_string.append(parent.letter_trie.find_key(input_line))
            if self.input_string[-1] == NO_SYMBOL_NUMBER:
                self.input_string.clear()
                break
        self.input_string.append(NO_SYMBOL_NUMBER)

class Result:
    def __init__(self, symbols: List[str], weight: float):
        self.symbols = symbols
        self.weight = weight
        
    def get_symbols(self) -> List[str]:
        return self.symbols
    
    def get_weight(self) -> float:
        return self.weight
    
    def __str__(self) -> str:
        return str(self.symbols) + ": " + str(self.weight)