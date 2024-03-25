from typing import List, Generator, Any, Tuple, Union, Optional
import io
from collections.abc import ByteString
from collections import defaultdict
from .byte_array import ByteArray


TRANSITION_TARGET_TABLE_START = 2147483648  # 2^31 or UINT_MAX/2 rounded up
# this is hopefully the same as static_cast<float>(UINT_MAX) in C++
INFINITE_WEIGHT = float(4294967295)
NO_SYMBOL_NUMBER = 65535  # USHRT_MAX
NO_TABLE_INDEX = 4294967295


class IndexTable:
    """
    A table to store input symbols and their corresponding target indices.
    """

    def __init__(self, input_stream: io.BytesIO, indices_count: int):
        b = ByteArray(indices_count * 6)
        input_stream.readinto(b.bytes)
        self.ti_input_symbols: List[int] = [0] * indices_count
        self.ti_targets: List[int] = [0] * indices_count
        for i in range(indices_count):
            self.ti_input_symbols[i] = b.get_ushort()
            self.ti_targets[i] = b.get_uint()

    def get_input(self, i: int) -> int:
        """
        Returns the input symbol at the given index.

        :param i: The index to retrieve the input symbol from.
        :return: The input symbol at the specified index.
        """
        return self.ti_input_symbols[i]

    def get_target(self, i: int) -> int:
        """
        Returns the target index at the given index.

        :param i: The index to retrieve the target index from.
        :return: The target index at the specified index.
        """
        return self.ti_targets[i]

    def is_final(self, i: int) -> bool:
        """
        Checks if the given index is a final state.

        :param i: The index to check.
        :return: True if the index is a final state, False otherwise.
        """
        return (
            self.ti_input_symbols[i] == NO_SYMBOL_NUMBER
            and self.ti_targets[i] != NO_TABLE_INDEX
        )

    def get_final_weight(self, i: int) -> float:
        """
        Returns the final weight for the given index.

        :param i: The index to retrieve the final weight from.
        :return: The final weight at the specified index.
        """
        return float(self.ti_targets[i])


class TransitionTable:
    """
    A table to store transitions between states.
    """

    def __init__(
        self, input_stream: io.BytesIO, transition_count: int, is_weighted: bool = True
    ):
        block_size = 12 if is_weighted else 8
        b = ByteArray(transition_count * block_size)
        input_stream.readinto(b.bytes)
        self.is_weighted: bool = is_weighted
        self.ti_input_symbols: List[int] = [0] * transition_count
        self.ti_output_symbols: List[int] = [0] * transition_count
        self.ti_targets: List[int] = [0] * transition_count
        self.ti_weights: List[float] = [0.0] * transition_count

        for i in range(transition_count):
            self.ti_input_symbols[i] = b.get_ushort()
            self.ti_output_symbols[i] = b.get_ushort()
            self.ti_targets[i] = b.get_uint()
            if self.is_weighted:
                self.ti_weights[i] = b.get_float()

    def get_input(self, pos: int) -> int:
        """
        Returns the input symbol at the given position.

        :param pos: The position to retrieve the input symbol from.
        :return: The input symbol at the specified position.
        """
        return self.ti_input_symbols[pos]

    def get_output(self, pos: int) -> int:
        """
        Returns the output symbol at the given position.

        :param pos: The position to retrieve the output symbol from.
        :return: The output symbol at the specified position.
        """
        return self.ti_output_symbols[pos]

    def get_target(self, pos: int) -> int:
        """
        Returns the target index at the given position.

        :param pos: The position to retrieve the target index from.
        :return: The target index at the specified position.
        """
        return self.ti_targets[pos]

    def get_weight(self, pos: int) -> float:
        """
        Returns the weight at the given position.

        :param pos: The position to retrieve the weight from.
        :return: The weight at the specified position.
        :raises Exception: If the transition table is unweighted.
        """
        if not self.is_weighted:
            raise Exception("Getting weights of unweighted FST.")
        return self.ti_weights[pos]

    def is_final(self, pos: int) -> bool:
        """
        Checks if the given position is a final state.
        :param pos: The position to check.
        :return: True if the position is a final state, False otherwise.
        """
        return (
            self.ti_input_symbols[pos] == NO_SYMBOL_NUMBER
            and self.ti_output_symbols[pos] == NO_SYMBOL_NUMBER
            and self.ti_targets[pos] == 1
        )

    def size(self) -> int:
        """
        Returns the size of the transition table.

        :return: The size of the transition table.
        """
        return len(self.ti_targets)


class State:
    """
    A class representing the state of the FST.
    """

    def __init__(self, input: str, parent: Any):
        self.parent: Any = parent
        self.state_stack: List[List[int]] = []
        neutral: List[int] = [0] * parent.alphabet.features
        self.state_stack.append(neutral)
        self.output_string: List[int] = [NO_SYMBOL_NUMBER] * 1000
        self.input_string: List[int] = list(self.find_key(input))
        self.output_pointer: int = 0
        self.input_pointer: int = 0
        self.current_weight: float = 0.0
        self.display_vector: List[int] = []

    def find_key(self, index_string: str) -> Generator[int, None, None]:
        """
        Finds the key associated with the given index string.
        :param index_string: The index string to search for.
        :return: The symbol number if found, otherwise NO_SYMBOL_NUMBER.
        """

        i = 0

        while i < len(index_string):
            match_found = False
            for length in range(len(index_string) - i, 0, -1):
                substr = index_string[i : i + length]
                map_pointer = self.parent.symbol_map
                for char in substr:
                    if char in map_pointer:
                        map_pointer = map_pointer[char]
                    else:
                        break
                else:
                    if None in map_pointer:
                        yield map_pointer[None]
                        i += length - 1
                        match_found = True
                    break
            if not match_found:
                yield NO_SYMBOL_NUMBER
            i += 1

        yield NO_SYMBOL_NUMBER


class Result:
    """
    A class representing a result with symbols and a weight.
    """

    def __init__(self, symbols: List[str], weight: float):
        self.symbols: List[str] = symbols
        self.weight: float = weight

    def get_symbols(self) -> List[str]:
        """
        Returns the list of symbols in the result.

        :return: The list of symbols.
        """
        return self.symbols

    def get_weight(self) -> float:
        """
        Returns the weight associated with the result.

        :return: The weight of the result.
        """
        return self.weight

    def __str__(self) -> str:
        """
        Returns a string representation of the result.

        :return: A string representation of the result in the format (text: weight).
        """
        return "".join(self.symbols) + ": " + str(self.weight)
