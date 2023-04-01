from .common import *
from .flag_diacritic_operation import FlagDiacriticOperation, FlagDiacriticOperator
from .transducer_header import TransducerHeader
from .transducer_alphabet import TransducerAlphabet


class Transducer:
    """
    A class representing a finite state transducer for morphological analysis.
    """

    def __init__(self, file, h: TransducerHeader, a: TransducerAlphabet, is_weighted: bool = True) -> None:
        """
        Initializes the Transducer instance.

        :param file: A file containing the transducer data.
        :param h: A TransducerHeader instance representing the header of the transducer.
        :param a: A TransducerAlphabet instance representing the alphabet of the transducer.
        :param is_weighted: A boolean indicating if the transducer is weighted. Defaults to True.
        """
        self.header = h
        self.alphabet = a
        self.is_weighted = is_weighted
        self.operations = self.alphabet.operations
        self.letter_trie = LetterTrie()
        for i in range(h.get_input_symbol_count()):
            self.letter_trie.add_string(self.alphabet.keyTable[i], i)
        self.index_table = IndexTable(file, h.get_index_table_size())
        self.transition_table = TransitionTable(
            file, h.get_target_table_size(), is_weighted=self.is_weighted)

    def pivot(self, i: int) -> int:
        """
        Computes the pivot for the given index.

        :param i: The index to compute the pivot for.
        :return: The pivot value.
        """
        if i >= TRANSITION_TARGET_TABLE_START:
            return i - TRANSITION_TARGET_TABLE_START
        return i

    def try_epsilon_indices(self, index: int, state: State) -> None:
        """
        Tries epsilon indices for the given index and state.

        :param index: The index to try epsilon indices for.
        :param state: The current state of the transducer.
        """
        if self.index_table.get_input(index) == 0:
            self.try_epsilon_transitions(self.pivot(
                self.index_table.get_target(index)), state)

    def try_epsilon_transitions(self, index: int, state: State) -> None:
        """
        Tries epsilon transitions for the given index and state.

        :param index: The index to try epsilon transitions for.
        :param state: The current state of the transducer.
        """
        while True:
            if self.operations.get(self.transition_table.get_input(index)):
                if not self.push_state(self.operations[self.transition_table.get_input(index)], state):
                    index += 1
                    continue
                else:
                    state.output_string[state.output_pointer] = self.transition_table.get_output(
                        index)
                    state.output_pointer += 1
                    if self.is_weighted:
                        state.current_weight += self.transition_table.get_weight(
                            index)
                    self.get_analyses(
                        self.transition_table.get_target(index), state)
                    if self.is_weighted:
                        state.current_weight -= self.transition_table.get_weight(
                            index)
                    state.output_pointer -= 1
                    index += 1
                    state.state_stack.pop()
                    continue
            elif self.transition_table.get_input(index) == 0:
                state.output_string[state.output_pointer] = self.transition_table.get_output(
                    index)
                state.output_pointer += 1
                if self.is_weighted:
                    state.current_weight += self.transition_table.get_weight(
                        index)
                self.get_analyses(
                    self.transition_table.get_target(index), state)
                if self.is_weighted:
                    state.current_weight -= self.transition_table.get_weight(
                        index)
                state.output_pointer -= 1
                index += 1
                continue
            else:
                break

    def find_index(self, index: int, state: State) -> None:
        """
        Finds the index in the transducer for the given index and state.

        :param index: The index to find in the transducer.
        :param state: The current state of the transducer.
        """
        if self.index_table.get_input(index + (state.input_string[state.input_pointer - 1])) == state.input_string[state.input_pointer - 1]:
            self.find_transitions(self.pivot(self.index_table.get_target(
                index + state.input_string[state.input_pointer - 1])), state)

    def find_transitions(self, index: int, state: State) -> None:
        """
        Finds the transitions in the transducer for the given index and state.

        :param index: The index to find transitions for.
        :param state: The current state of the transducer.
        """
        while self.transition_table.get_input(index) != NO_SYMBOL_NUMBER:
            if self.transition_table.get_input(index) == state.input_string[state.input_pointer - 1]:
                if state.output_pointer == len(state.output_string):
                    state.output_string.append(
                        self.transition_table.get_output(index))
                else:
                    state.output_string[state.output_pointer] = self.transition_table.get_output(
                        index)
                state.output_pointer += 1
                if self.is_weighted:
                    state.current_weight += self.transition_table.get_weight(
                        index)
                self.get_analyses(
                    self.transition_table.get_target(index), state)
                if self.is_weighted:
                    state.current_weight -= self.transition_table.get_weight(
                        index)
                state.output_pointer -= 1
            else:
                return
            index += 1

    def get_analyses(self, idx: int, state: State) -> None:
        """
        Gets the analyses for the given index and state.

        :param idx: The index to get the analyses for.
        :param state: The current state of the transducer.
        """
        if idx >= TRANSITION_TARGET_TABLE_START:
            index = self.pivot(idx)
            self.try_epsilon_transitions(index + 1, state)
            # end of input string
            if state.input_string[state.input_pointer] == NO_SYMBOL_NUMBER:
                if state.output_pointer == len(state.output_string):
                    state.output_string.append(NO_SYMBOL_NUMBER)
                else:
                    state.output_string[state.output_pointer] = NO_SYMBOL_NUMBER
                if self.transition_table.size() > index and self.transition_table.is_final(index):
                    if self.is_weighted:
                        state.current_weight += self.transition_table.get_weight(
                            index)
                    self.note_analysis(state)
                    if self.is_weighted:
                        state.current_weight -= self.transition_table.get_weight(
                            index)
                return
            state.input_pointer += 1
            self.find_transitions(index + 1, state)
        else:
            index = self.pivot(idx)
            self.try_epsilon_indices(index + 1, state)
            # end of input string
            if state.input_string[state.input_pointer] == NO_SYMBOL_NUMBER:
                if state.output_pointer == len(state.output_string):
                    state.output_string.append(NO_SYMBOL_NUMBER)
                else:
                    state.output_string[state.output_pointer] = NO_SYMBOL_NUMBER
                if self.index_table.is_final(index):
                    if self.is_weighted:
                        state.current_weight += self.index_table.get_final_weight(
                            index)
                    self.note_analysis(state)
                    if self.is_weighted:
                        state.current_weight -= self.index_table.get_final_weight(
                            index)
                return
            state.input_pointer += 1
            self.find_index(index + 1, state)
        state.input_pointer -= 1
        if state.output_pointer == len(state.output_string):
            state.output_string.append(NO_SYMBOL_NUMBER)
        else:
            state.output_string[state.output_pointer] = NO_SYMBOL_NUMBER

    def get_symbols(self, state: State) -> List[str]:
        """
        Gets the symbols for the given state.

        :param state: The current state of the transducer.
        :return: A list of symbols.
        """
        i = 0
        symbols = []
        while i < len(state.output_string) and state.output_string[i] != NO_SYMBOL_NUMBER:
            symbols.append(self.alphabet.keyTable[state.output_string[i]])
            i += 1
        return symbols

    def note_analysis(self, state: State) -> None:
        """
        Notes the analysis for the given state.

        :param state: The current state of the transducer.
        """
        state.display_vector.append(Result(self.get_symbols(
            state), state.current_weight if self.is_weighted else 1.0))

    def get_alphabet(self) -> List[str]:
        """
        Gets the alphabet of the transducer.

        :return: A list of alphabet symbols.
        """
        return self.alphabet.keyTable

    def analyze(self, input: str) -> List['Transducer.Result']:
        """
        Analyzes the input string using the transducer.

        :param input: The input string to analyze.
        :return: A list of Result instances representing the analyses of the input string.
        """
        state = State(input, self)
        if state.input_string[0] == NO_SYMBOL_NUMBER:
            return []
        self.get_analyses(0, state)
        return state.display_vector

    def push_state(self, flag: FlagDiacriticOperation, state: State) -> bool:
        """
        Pushes the state based on the given flag diacritic operation and the current state.

        :param flag: A FlagDiacriticOperation instance representing the flag diacritic operation.
        :param state: The current state of the transducer.
        :return: A boolean indicating if the push was successful.
        """
        top = state.state_stack[-1].copy()
        if flag.op == FlagDiacriticOperator.P:  # positive set
            state.state_stack.append(top)
            state.state_stack[-1][flag.feature] = flag.value
            return True
        elif flag.op == FlagDiacriticOperator.N:  # negative set
            state.state_stack.append(top)
            state.state_stack[-1][flag.feature] = -1 * flag.value
            return True
        elif flag.op == FlagDiacriticOperator.R:  # require
            if flag.value == 0:  # empty require
                if state.state_stack[-1][flag.feature] == 0:
                    return False
                else:
                    state.state_stack.append(top)
                    return True
            elif state.state_stack[-1][flag.feature] == flag.value:
                state.state_stack.append(top)
                return True
            return False
        elif flag.op == FlagDiacriticOperator.D:  # disallow
            if flag.value == 0:  # empty disallow
                if state.state_stack[-1][flag.feature] != 0:
                    return False
                else:
                    state.state_stack.append(top)
                    return True
            elif state.state_stack[-1][flag.feature] == flag.value:
                return False
            else:
                state.state_stack.append(top)
                return True
        elif flag.op == FlagDiacriticOperator.C:  # clear
            state.state_stack.append(top)
            state.state_stack[-1][flag.feature] = 0
            return True
        elif flag.op == FlagDiacriticOperator.U:  # unification
            if (state.state_stack[-1][flag.feature] == 0) or (state.state_stack[-1][flag.feature] == flag.value) or (state.state_stack[-1][flag.feature] != flag.value and state.state_stack[-1][flag.feature] < 0):
                state.state_stack.append(top)
                state.state_stack[-1][flag.feature] = flag.value
                return True
            return False
        return False  # compiler sanity
