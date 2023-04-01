from .common import * 
from .flag_diacritic_operation import FlagDiacriticOperation, FlagDiacriticOperator
from .transducer_header import TransducerHeader
from .transducer_alphabet import TransducerAlphabet

class Transducer:
    def __init__(self, file, h: TransducerHeader, a: TransducerAlphabet, is_weighted=True) -> None:
        self.header = h
        self.alphabet = a
        self.is_weighted = is_weighted
        self.operations = self.alphabet.operations
        self.letter_trie = LetterTrie()
        for i in range(h.get_input_symbol_count()):
            self.letter_trie.add_string(self.alphabet.keyTable[i], i)
        self.index_table = IndexTable(file, h.get_index_table_size())
        self.transition_table = TransitionTable(file, h.get_target_table_size(), is_weighted=self.is_weighted)

    def pivot(self, i):
        if i >= TRANSITION_TARGET_TABLE_START:
            return i - TRANSITION_TARGET_TABLE_START
        return i

    def try_epsilon_indices(self, index: int, state: State):
        if self.index_table.get_input(index) == 0:
            self.try_epsilon_transitions(self.pivot(self.index_table.get_target(index)), state)

    def try_epsilon_transitions(self, index: int, state: State):
        while True:
            if self.operations.get(self.transition_table.get_input(index)):
                if not self.push_state(self.operations[self.transition_table.get_input(index)], state):
                    index += 1
                    continue
                else:
                    state.output_string[state.output_pointer] = self.transition_table.get_output(index)
                    state.output_pointer += 1
                    if self.is_weighted: state.current_weight += self.transition_table.get_weight(index)
                    self.get_analyses(self.transition_table.get_target(index), state)
                    if self.is_weighted: state.current_weight -= self.transition_table.get_weight(index)
                    state.output_pointer -= 1
                    index += 1
                    state.state_stack.pop()
                    continue
            elif self.transition_table.get_input(index) == 0:
                state.output_string[state.output_pointer] = self.transition_table.get_output(index)
                state.output_pointer += 1
                if self.is_weighted: state.current_weight += self.transition_table.get_weight(index)
                self.get_analyses(self.transition_table.get_target(index), state)
                if self.is_weighted: state.current_weight -= self.transition_table.get_weight(index)
                state.output_pointer -= 1
                index += 1
                continue
            else:
                break

    def find_index(self, index, state):
        if self.index_table.get_input(index + (state.input_string[state.input_pointer - 1])) == state.input_string[state.input_pointer - 1]:
            self.find_transitions(self.pivot(self.index_table.get_target(index + state.input_string[state.input_pointer - 1])), state)

    def find_transitions(self, index: int, state: State):
        while self.transition_table.get_input(index) != NO_SYMBOL_NUMBER:
            if self.transition_table.get_input(index) == state.input_string[state.input_pointer - 1]:
                if state.output_pointer == len(state.output_string):
                    state.output_string.append(self.transition_table.get_output(index))
                else:
                    state.output_string[state.output_pointer] = self.transition_table.get_output(index)
                state.output_pointer += 1
                if self.is_weighted: state.current_weight += self.transition_table.get_weight(index)
                self.get_analyses(self.transition_table.get_target(index), state)
                if self.is_weighted: state.current_weight -= self.transition_table.get_weight(index)
                state.output_pointer -= 1
            else:
                return
            index += 1


    def get_analyses(self, idx, state: State):
        if idx >= TRANSITION_TARGET_TABLE_START:
            index = self.pivot(idx)
            self.try_epsilon_transitions(index + 1, state)
            if state.input_string[state.input_pointer] == NO_SYMBOL_NUMBER:  # end of input string
                if state.output_pointer == len(state.output_string):
                    state.output_string.append(NO_SYMBOL_NUMBER)
                else:
                    state.output_string[state.output_pointer] = NO_SYMBOL_NUMBER
                if self.transition_table.size() > index and self.transition_table.is_final(index):
                    if self.is_weighted: state.current_weight += self.transition_table.get_weight(index)
                    self.note_analysis(state)
                    if self.is_weighted: state.current_weight -= self.transition_table.get_weight(index)
                return
            state.input_pointer += 1
            self.find_transitions(index + 1, state)
        else:
            index = self.pivot(idx)
            self.try_epsilon_indices(index + 1, state)
            if state.input_string[state.input_pointer] == NO_SYMBOL_NUMBER:  # end of input string
                if state.output_pointer == len(state.output_string):
                    state.output_string.append(NO_SYMBOL_NUMBER)
                else:
                    state.output_string[state.output_pointer] = NO_SYMBOL_NUMBER
                if self.index_table.is_final(index):
                    if self.is_weighted: state.current_weight += self.index_table.get_final_weight(index)
                    self.note_analysis(state)
                    if self.is_weighted: state.current_weight -= self.index_table.get_final_weight(index)
                return
            state.input_pointer += 1
            self.find_index(index + 1, state)
        state.input_pointer -= 1
        if state.output_pointer == len(state.output_string):
            state.output_string.append(NO_SYMBOL_NUMBER)
        else:
            state.output_string[state.output_pointer] = NO_SYMBOL_NUMBER

    def get_symbols(self, state: State):
        i = 0
        symbols = []
        while i < len(state.output_string) and state.output_string[i] != NO_SYMBOL_NUMBER:
            symbols.append(self.alphabet.keyTable[state.output_string[i]])
            i += 1
        return symbols
    
    def note_analysis(self, state: State):
        state.display_vector.append(Result(self.get_symbols(state), state.current_weight if self.is_weighted else 1.0))

    def get_alphabet(self):
        return self.alphabet.keyTable

    def analyze(self, input: str) -> List['Transducer.Result']:
        state = State(input, self)
        if state.input_string[0] == NO_SYMBOL_NUMBER:
            return []
        self.get_analyses(0, state)
        return state.display_vector

    def push_state(self, flag: FlagDiacriticOperation, state: State) -> bool:
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


