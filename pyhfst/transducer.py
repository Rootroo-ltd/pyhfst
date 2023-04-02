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
            input_symbol = self.transition_table.get_input(index)

            if self.operations.get(input_symbol):
                if self.push_state(self.operations[input_symbol], state):
                    self.handle_epsilon_transition(index, state)
                index += 1
                state.state_stack.pop()
                continue
            elif input_symbol == 0:
                self.handle_epsilon_transition(index, state)
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

    def handle_epsilon_transition(self, index: int, state: State) -> None:
        """
        Handles epsilon transitions for the given index and state.

        :param index: The index to handle epsilon transitions for.
        :param state: The current state of the transducer.
        """
        self.update_output_string(
            state, self.transition_table.get_output(index))
        state.output_pointer += 1

        if self.is_weighted:
            state.current_weight += self.transition_table.get_weight(index)

        self.get_analyses(self.transition_table.get_target(index), state)

        if self.is_weighted:
            state.current_weight -= self.transition_table.get_weight(index)

        state.output_pointer -= 1

    def find_transitions(self, index: int, state: State) -> None:
        """
        Finds the transitions in the transducer for the given index and state.

        :param index: The index to find transitions for.
        :param state: The current state of the transducer.
        """
        for idx in range(index, self.transition_table.size()):
            input_symbol = self.transition_table.get_input(idx)
            if input_symbol == NO_SYMBOL_NUMBER:
                break

            if input_symbol == state.input_string[state.input_pointer - 1]:
                self.update_output_string(
                    state, self.transition_table.get_output(idx))
                state.output_pointer += 1

                if self.is_weighted:
                    state.current_weight += self.transition_table.get_weight(
                        idx)

                self.get_analyses(self.transition_table.get_target(idx), state)

                if self.is_weighted:
                    state.current_weight -= self.transition_table.get_weight(
                        idx)

                state.output_pointer -= 1

    def get_analyses(self, idx: int, state: State) -> None:
        """
        Gets the analyses for the given index and state.

        :param idx: The index to get the analyses for.
        :param state: The current state of the transducer.
        """
        index = self.pivot(idx)
        is_transition = idx >= TRANSITION_TARGET_TABLE_START

        if is_transition:
            self.try_epsilon_transitions(index + 1, state)
        else:
            self.try_epsilon_indices(index + 1, state)

        if state.input_string[state.input_pointer] == NO_SYMBOL_NUMBER:
            self.handle_end_of_input_string(state, index, is_transition)
            return

        state.input_pointer += 1

        if is_transition:
            self.find_transitions(index + 1, state)
        else:
            self.find_index(index + 1, state)

        state.input_pointer -= 1
        self.reset_output_pointer(state)

    def update_output_string(self, state: State, output_symbol: int) -> None:
        """
        Updates the output string in the state based on the output symbol.

        :param state: The current state of the transducer.
        :param output_symbol: The output symbol to append or update in the output string.
        """
        if state.output_pointer == len(state.output_string):
            state.output_string.append(output_symbol)
        else:
            state.output_string[state.output_pointer] = output_symbol

    def handle_end_of_input_string(self, state: State, index: int, is_transition: bool) -> None:
        """
        Handles the end of the input string.

        :param state: The current state of the transducer.
        :param index: The index being processed.
        :param is_transition: A boolean indicating whether it's a transition table or an index table.
        """
        self.reset_output_pointer(state)

        is_final, weight = self.get_final_and_weight(index, is_transition)
        if is_final:
            self.update_and_note_analysis(state, weight)

    def reset_output_pointer(self, state: State) -> None:
        """
        Resets the output pointer in the state.

        :param state: The current state of the transducer.
        """
        if state.output_pointer == len(state.output_string):
            state.output_string.append(NO_SYMBOL_NUMBER)
        else:
            state.output_string[state.output_pointer] = NO_SYMBOL_NUMBER

    def get_final_and_weight(self, index: int, is_transition: bool) -> Tuple[bool, float]:
        """
        Gets the final state and weight based on the index and transition flag.

        :param index: The index being processed.
        :param is_transition: A boolean indicating whether it's a transition table or an index table.
        :return: A tuple containing a boolean for final state and a float for the weight.
        """
        if is_transition:
            is_final = self.transition_table.size(
            ) > index and self.transition_table.is_final(index)
            weight = self.transition_table.get_weight(
                index) if self.is_weighted else 0
        else:
            is_final = self.index_table.is_final(index)
            weight = self.index_table.get_final_weight(
                index) if self.is_weighted else 0

        return is_final, weight

    def update_and_note_analysis(self, state: State, weight: float) -> None:
        """
        Updates the state's current weight and notes the analysis.

        :param state: The current state of the transducer.
        :param weight: The weight to be
        """
        if self.is_weighted:
            state.current_weight += weight
        self.note_analysis(state)
        if self.is_weighted:
            state.current_weight -= weight

    def get_symbols(self, state: State) -> List[str]:
        """
        Gets the symbols for the given state.

        :param state: The current state of the transducer.
        :return: A list of symbols.
        """
        symbols = [self.alphabet.keyTable[state.output_string[i]] for i in range(
            len(state.output_string)) if state.output_string[i] != NO_SYMBOL_NUMBER]
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
        else:
            self.get_analyses(0, state)
            return state.display_vector

    def push_state(self, flag: FlagDiacriticOperation, state: State) -> bool:
        """
        Pushes the state based on the given flag diacritic operation and the current state.

        :param flag: A FlagDiacriticOperation instance representing the flag diacritic operation.
        :param state: The current state of the transducer.
        :return: A boolean indicating if the push was successful.
        """
        top = state.state_stack[-1]
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
