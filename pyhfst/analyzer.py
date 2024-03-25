from .common import *
from .transducer import Transducer
from .flag_diacritic_operation import FlagDiacriticOperation, FlagDiacriticOperator


class Analyzer:
    def __init__(self, transducer: Transducer, input_str: str):
        self.transducer = transducer
        self.input_str = input_str
        self.state = State(input_str, self.transducer)

    def pivot(self, i: int) -> int:
        """
        Computes the pivot for the given index.

        :param i: The index to compute the pivot for.
        :return: The pivot value.
        """
        if i >= TRANSITION_TARGET_TABLE_START:
            return i - TRANSITION_TARGET_TABLE_START
        return i

    def try_epsilon_indices(self, index: int) -> None:
        """
        Tries epsilon indices for the given index and state.

        :param index: The index to try epsilon indices for.
        :param state: The current state of the transducer.
        """
        if self.transducer.index_table.get_input(index) == 0:
            self.try_epsilon_transitions(
                self.pivot(self.transducer.index_table.get_target(index))
            )

    def try_epsilon_transitions(self, index: int) -> None:
        """
        Tries epsilon transitions for the given index and state.

        :param index: The index to try epsilon transitions for.
        :param state: The current state of the transducer.
        """
        while True:
            input_symbol = self.transducer.transition_table.get_input(index)

            if self.transducer.operations.get(input_symbol):
                if not self.push_state(self.transducer.operations[input_symbol]):
                    index += 1
                    continue
                self.handle_epsilon_transition(index)
                index += 1
                self.state.state_stack.pop()
                continue
            elif input_symbol == 0:
                self.handle_epsilon_transition(index)
                index += 1
                continue
            else:
                break

    def find_index(self, index: int) -> None:
        """
        Finds the index in the transducer for the given index and state.

        :param index: The index to find in the transducer.
        :param state: The current state of the transducer.
        """
        if (
            self.transducer.index_table.get_input(
                index + (self.state.input_string[self.state.input_pointer - 1])
            )
            == self.state.input_string[self.state.input_pointer - 1]
        ):
            self.find_transitions(
                self.pivot(
                    self.transducer.index_table.get_target(
                        index + self.state.input_string[self.state.input_pointer - 1]
                    )
                )
            )

    def handle_epsilon_transition(self, index: int) -> None:
        """
        Handles epsilon transitions for the given index and state.

        :param index: The index to handle epsilon transitions for.
        :param state: The current state of the transducer.
        """
        self.update_output_string(self.transducer.transition_table.get_output(index))
        self.state.output_pointer += 1

        if self.transducer.is_weighted:
            self.state.current_weight += self.transducer.transition_table.get_weight(
                index
            )

        self.get_analyses(self.transducer.transition_table.get_target(index))

        if self.transducer.is_weighted:
            self.state.current_weight -= self.transducer.transition_table.get_weight(
                index
            )

        self.state.output_pointer -= 1

    def find_transitions(self, index: int) -> None:
        """
        Finds the transitions in the transducer for the given index and state.

        :param index: The index to find transitions for.
        :param state: The current state of the transducer.
        """
        for idx in range(index, self.transducer.transition_table.size()):
            input_symbol = self.transducer.transition_table.get_input(idx)

            if input_symbol == NO_SYMBOL_NUMBER:
                break

            if input_symbol == self.state.input_string[self.state.input_pointer - 1]:
                self.update_output_string(
                    self.transducer.transition_table.get_output(idx)
                )
                self.state.output_pointer += 1

                if self.transducer.is_weighted:
                    self.state.current_weight += (
                        self.transducer.transition_table.get_weight(idx)
                    )

                self.get_analyses(self.transducer.transition_table.get_target(idx))

                if self.transducer.is_weighted:
                    self.state.current_weight -= (
                        self.transducer.transition_table.get_weight(idx)
                    )

                self.state.output_pointer -= 1
            else:
                break

    def get_analyses(self, idx: int) -> None:
        """
        Gets the analyses for the given index and state.

        :param idx: The index to get the analyses for.
        :param state: The current state of the transducer.
        """
        index = self.pivot(idx)
        is_transition = idx >= TRANSITION_TARGET_TABLE_START

        if is_transition:
            next_v = self.pivot(index) if self.transducer.is_weighted else index
            self.try_epsilon_transitions(next_v + 1)
        else:
            self.try_epsilon_indices(index + 1)

        if self.state.input_string[self.state.input_pointer] == NO_SYMBOL_NUMBER:
            self.handle_end_of_input_string(index, is_transition)
            return

        self.state.input_pointer += 1

        if is_transition:
            self.find_transitions(index + 1)
        else:
            self.find_index(index + 1)

        self.state.input_pointer -= 1
        self.reset_output_pointer()

    def update_output_string(self, output_symbol: int) -> None:
        """
        Updates the output string in the state based on the output symbol.

        :param state: The current state of the transducer.
        :param output_symbol: The output symbol to append or update in the output string.
        """
        if self.state.output_pointer == len(self.state.output_string):
            self.state.output_string.append(output_symbol)
        else:
            self.state.output_string[self.state.output_pointer] = output_symbol

    def handle_end_of_input_string(self, index: int, is_transition: bool) -> None:
        """
        Handles the end of the input string.

        :param state: The current state of the transducer.
        :param index: The index being processed.
        :param is_transition: A boolean indicating whether it's a transition table or an index table.
        """
        self.reset_output_pointer()

        is_final, weight = self.get_final_and_weight(index, is_transition)
        if is_final:
            self.update_and_note_analysis(weight)

    def reset_output_pointer(self) -> None:
        """
        Resets the output pointer in the state.

        :param state: The current state of the transducer.
        """
        if self.state.output_pointer == len(self.state.output_string):
            self.state.output_string.append(NO_SYMBOL_NUMBER)
        else:
            self.state.output_string[self.state.output_pointer] = NO_SYMBOL_NUMBER

    def get_final_and_weight(
        self, index: int, is_transition: bool
    ) -> Tuple[bool, float]:
        """
        Gets the final state and weight based on the index and transition flag.

        :param index: The index being processed.
        :param is_transition: A boolean indicating whether it's a transition table or an index table.
        :return: A tuple containing a boolean for final state and a float for the weight.
        """
        if is_transition:
            is_final = (
                self.transducer.transition_table.size() > index
                and self.transducer.transition_table.is_final(index)
            )
            weight = (
                self.transducer.transition_table.get_weight(index)
                if self.transducer.is_weighted
                else 0
            )
        else:
            is_final = self.transducer.index_table.is_final(index)
            weight = (
                self.transducer.index_table.get_final_weight(index)
                if self.transducer.is_weighted
                else 0
            )

        return is_final, weight

    def update_and_note_analysis(self, weight: float) -> None:
        """
        Updates the state's current weight and notes the analysis.

        :param state: The current state of the transducer.
        :param weight: The weight to be
        """
        if self.transducer.is_weighted:
            self.state.current_weight += weight
        self.note_analysis()
        if self.transducer.is_weighted:
            self.state.current_weight -= weight

    def get_symbols(self) -> List[str]:
        """
        Gets the symbols for the given state.

        :param state: The current state of the transducer.
        :return: A list of symbols.
        """
        symbols = [
            self.transducer.alphabet.keyTable[self.state.output_string[i]]
            for i in range(len(self.state.output_string))
            if self.state.output_string[i] != NO_SYMBOL_NUMBER
        ]
        return symbols

    def note_analysis(self) -> None:
        """
        Notes the analysis for the given state.

        :param state: The current state of the transducer.
        """
        self.state.display_vector.append(
            Result(
                self.get_symbols(),
                self.state.current_weight if self.transducer.is_weighted else 1.0,
            )
        )

    def get_alphabet(self) -> List[str]:
        """
        Gets the alphabet of the transducer.

        :return: A list of alphabet symbols.
        """
        return self.transducer.alphabet.keyTable

    def analyze(self) -> List["Result"]:
        """
        Analyzes the input string using the transducer.

        :param input: The input string to analyze.
        :return: A list of Result instances representing the analyses of the input string.
        """
        if self.state.input_string[0] == NO_SYMBOL_NUMBER:
            return []
        else:
            self.get_analyses(0)
            return self.state.display_vector

    def push_state(self, flag: FlagDiacriticOperation) -> bool:
        """
        Pushes the state based on the given flag diacritic operation and the current state.

        :param flag: A FlagDiacriticOperation instance representing the flag diacritic operation.
        :param state: The current state of the transducer.
        :return: A boolean indicating if the push was successful.
        """
        top = self.state.state_stack[-1].copy()
        if flag.op == FlagDiacriticOperator.P:  # positive set
            self.state.state_stack.append(top)
            self.state.state_stack[-1][flag.feature] = flag.value
            return True
        elif flag.op == FlagDiacriticOperator.N:  # negative set
            self.state.state_stack.append(top)
            self.state.state_stack[-1][flag.feature] = -1 * flag.value
            return True
        elif flag.op == FlagDiacriticOperator.R:  # require
            if flag.value == 0:  # empty require
                if self.state.state_stack[-1][flag.feature] == 0:
                    return False
                else:
                    self.state.state_stack.append(top)
                    return True
            elif self.state.state_stack[-1][flag.feature] == flag.value:
                self.state.state_stack.append(top)
                return True
            return False
        elif flag.op == FlagDiacriticOperator.D:  # disallow
            if flag.value == 0:  # empty disallow
                if self.state.state_stack[-1][flag.feature] != 0:
                    return False
                else:
                    self.state.state_stack.append(top)
                    return True
            elif self.state.state_stack[-1][flag.feature] == flag.value:
                return False
            else:
                self.state.state_stack.append(top)
                return True
        elif flag.op == FlagDiacriticOperator.C:  # clear
            self.state.state_stack.append(top)
            self.state.state_stack[-1][flag.feature] = 0
            return True
        elif flag.op == FlagDiacriticOperator.U:  # unification
            if (
                (self.state.state_stack[-1][flag.feature] == 0)
                or (self.state.state_stack[-1][flag.feature] == flag.value)
                or (
                    self.state.state_stack[-1][flag.feature] != flag.value
                    and self.state.state_stack[-1][flag.feature] < 0
                )
            ):
                self.state.state_stack.append(top)
                self.state.state_stack[-1][flag.feature] = flag.value
                return True
            return False
        return False  # compiler sanity
