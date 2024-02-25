# cython: language_level=3
from .common cimport *
from .flag_diacritic_operation cimport FlagDiacriticOperation, FlagDiacriticOperator
from .transducer import Transducer

cdef class Analyzer:

    def __cinit__(self, transducer: Transducer, input_str: str):
        self.transducer = transducer
        self.input_str = input_str
        self.state = State(input_str, self.transducer)

    cpdef cython.longlong pivot(self, cython.longlong i):
        """
        Computes the pivot for the given index.

        :param i: The index to compute the pivot for.
        :return: The pivot value.
        """
        if i >= TRANSITION_TARGET_TABLE_START:
            return (i - TRANSITION_TARGET_TABLE_START) % TRANSITION_TARGET_TABLE_START
        return i

    cpdef void try_epsilon_indices(self, cython.longlong index):
        """
        Tries epsilon indices for the given index and state.

        :param index: The index to try epsilon indices for.
        :param state: The current state of the transducer.
        """
        if self.transducer.index_table.get_input(index) == 0:
            self.try_epsilon_transitions(self.pivot(
                self.transducer.index_table.get_target(index)))

    cpdef void try_epsilon_transitions(self, cython.longlong index):
        """
        Tries epsilon transitions for the given index and state.

        :param index: The index to try epsilon transitions for.
        :param state: The current state of the transducer.
        """
        cdef cython.longlong input_symbol

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

    cpdef void find_index(self, cython.longlong index):
        """
        Finds the index in the transducer for the given index and state.

        :param index: The index to find in the transducer.
        :param state: The current state of the transducer.
        """
        if self.transducer.index_table.get_input(index + (self.state.input_string[self.state.input_pointer - 1])) == self.state.input_string[self.state.input_pointer - 1]:
            self.find_transitions(self.pivot(self.transducer.index_table.get_target(
                index + self.state.input_string[self.state.input_pointer - 1])))

    cpdef void handle_epsilon_transition(self, cython.longlong index):
        """
        Handles epsilon transitions for the given index and state.

        :param index: The index to handle epsilon transitions for.
        :param state: The current state of the transducer.
        """
        self.update_output_string(self.transducer.transition_table.get_output(index))
        self.state.output_pointer += 1

        if self.transducer.is_weighted:
            self.state.current_weight += self.transducer.transition_table.get_weight(index)

        self.get_analyses(self.transducer.transition_table.get_target(index))

        if self.transducer.is_weighted:
            self.state.current_weight -= self.transducer.transition_table.get_weight(index)

        self.state.output_pointer -= 1

    cpdef void find_transitions(self, cython.longlong index):
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
                self.update_output_string(self.transducer.transition_table.get_output(idx))
                self.state.output_pointer += 1

                if self.transducer.is_weighted:
                    self.state.current_weight += self.transducer.transition_table.get_weight(
                        idx)

                self.get_analyses(self.transducer.transition_table.get_target(idx))

                if self.transducer.is_weighted:
                    self.state.current_weight -= self.transducer.transition_table.get_weight(
                        idx)

                self.state.output_pointer -= 1
            else:
                break

    cpdef void get_analyses(self, cython.longlong idx):
        """
        Gets the analyses for the given index and state.

        :param idx: The index to get the analyses for.
        :param state: The current state of the transducer.
        """
        cdef cython.longlong index = self.pivot(idx)
        is_transition = idx >= TRANSITION_TARGET_TABLE_START
        if is_transition:
            self.try_epsilon_transitions(self.pivot(index) + 1)
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

    cpdef void update_output_string(self, cython.longlong output_symbol):
        """
        Updates the output string in the state based on the output symbol.

        :param state: The current state of the transducer.
        :param output_symbol: The output symbol to append or update in the output string.
        """
        if self.state.output_pointer == len(self.state.output_string):
            self.state.output_string.append(output_symbol)
        else:
            self.state.output_string[self.state.output_pointer] = output_symbol

    cpdef void handle_end_of_input_string(self, cython.longlong index, bint is_transition):
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

    cpdef void reset_output_pointer(self):
        """
        Resets the output pointer in the state.

        :param state: The current state of the transducer.
        """
        if self.state.output_pointer == len(self.state.output_string):
            self.state.output_string.append(NO_SYMBOL_NUMBER)
        else:
            self.state.output_string[self.state.output_pointer] = NO_SYMBOL_NUMBER

    cpdef tuple get_final_and_weight(self, cython.longlong index, bint is_transition):
        """
        Gets the final state and weight based on the index and transition flag.

        :param index: The index being processed.
        :param is_transition: A boolean indicating whether it's a transition table or an index table.
        :return: A tuple containing a boolean for final state and a float for the weight.
        """
        if is_transition:
            is_final = self.transducer.transition_table.size(
            ) > index and self.transducer.transition_table.is_final(index)
            weight = self.transducer.transition_table.get_weight(
                index) if self.transducer.is_weighted else 0
        else:
            is_final = self.transducer.index_table.is_final(index)
            weight = self.transducer.index_table.get_final_weight(
                index) if self.transducer.is_weighted else 0

        return is_final, weight

    cpdef void update_and_note_analysis(self, float weight):
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

    cpdef list get_symbols(self):
        """
        Gets the symbols for the given state.

        :param state: The current state of the transducer.
        :return: A list of symbols.
        """
        symbols = [self.transducer.alphabet.keyTable[self.state.output_string[i]] for i in range(
            len(self.state.output_string)) if self.state.output_string[i] != NO_SYMBOL_NUMBER]
        return symbols

    cpdef void note_analysis(self):
        """
        Notes the analysis for the given state.

        :param state: The current state of the transducer.
        """
        self.state.display_vector.append(Result(self.get_symbols(), self.state.current_weight if self.transducer.is_weighted else 1.0))

    cpdef list get_alphabet(self):
        """
        Gets the alphabet of the transducer.

        :return: A list of alphabet symbols.
        """
        return self.transducer.alphabet.keyTable

    cpdef public list analyze(self):
        if self.state.input_string[0] == NO_SYMBOL_NUMBER:
            return []
        else:
            self.get_analyses(0)
            return self.state.display_vector

    cpdef bint push_state(self, FlagDiacriticOperation flag):
        cdef list top = self.state.state_stack[-1]
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
            if (self.state.state_stack[-1][flag.feature] == 0) or (self.state.state_stack[-1][flag.feature] == flag.value) or (self.state.state_stack[-1][flag.feature] != flag.value and self.state.state_stack[-1][flag.feature] < 0):
                self.state.state_stack.append(top)
                self.state.state_stack[-1][flag.feature] = flag.value
                return True
            return False
        return False  # compiler sanity
