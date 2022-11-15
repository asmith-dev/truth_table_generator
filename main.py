import math


class Table:
    def __init__(self, inp: str):
        # Constants
        self.WHITESPACE = " \t"
        self.OPS = "&|+!"
        self.BIN = "01"

        self.entries: list[str] = inp.split(";")
        self.map_entries = {}
        self.ast: list[list[list[list[str]]]] = []
        self.statements: list[str] = []
        self.map_statements = {}
        self.size = 0
        self.result = "\n"

    def __str__(self):
        return self.result

    # Number of binary permutations relative to the number of statements
    def set_size(self):
        self.size = 2**len(self.statements)

    def remove_character(self, entry: int, pointer: int):
        # If at the beginning
        if pointer == 0:
            self.entries[entry] = self.entries[entry][1:]

        # If at the end
        elif pointer == len(self.entries[entry])-1:
            self.entries[entry] = self.entries[entry][:-1]

        # If somewhere in the middle
        else:
            self.entries[entry] = self.entries[entry][:pointer] + self.entries[entry][pointer + 1:]

    def remove_whitespace(self):
        ptr = 0
        for i in range(len(self.entries)):
            while self.WHITESPACE[0] in self.entries[i] or self.WHITESPACE[1] in self.entries[i]:
                if self.entries[i][ptr] in self.WHITESPACE:
                    self.remove_character(i, ptr)
                else:
                    ptr += 1
            ptr = 0

    # A complicated, yet compact and efficient, algorithm for populating all the combinations
    def populate_statements(self):
        it = iter(self.statements)
        for n in [2**i for i in range(len(self.statements))]:
            self.map_statements[next(it)] = [math.floor(j * n * 2 / self.size) for j in range(int(self.size / n))] * n

    # This uses the table entries, statements, and their respective maps to create the table
    def generate(self):
        # Creates the top row with each column identifier
        for i in self.statements:
            self.result += f"| {i} "
        self.result += "||"
        for i in self.entries:
            self.result += f" {i} |"
        self.result += "\n"

        # Creates the dashed line separating the top identifiers with the bottom values
        for i in self.statements:
            self.result += "|" + "-" * (len(i)+2)
        self.result += "||"
        for i in self.entries:
            self.result += "-" * (len(i)+2) + "|"
        self.result += "\n"

        # Fills the table with 1s and 0s
        for i in range(self.size):
            for j in self.statements:
                left = " " * (1 + math.floor(len(j) / 2))
                right = " " * math.ceil(len(j) / 2)
                self.result += f"|{left}{self.map_statements[j][i]}{right}"
            self.result += "||"
            for j in self.entries:
                left = " " * (1 + math.floor(len(j) / 2))
                right = " " * math.ceil(len(j) / 2)
                self.result += f"{left}{self.map_entries[j][i]}{right}|"
            self.result += "\n"


class Parser:
    def __init__(self, table_input: Table):
        self.table = table_input

        self.entry = -1
        self.num_entries = len(self.table.entries)
        self.scope = 0
        self.eoe = 0  # end-of-entry
        self.ptr = 0  # input pointer
        self.ec = [0]  # expression count

        """
        self.grammar maps an input token to the options for what token it expects to come next
        
        B  -> Beginning of entry
        E  -> End of entry
        LP -> Left parenthesis
        RP -> Right parenthesis
        S  -> Statement
        O  -> Operator
        N  -> Not
        """
        self.grammar = {"B": ["LP", "S", "N"],
                        "LP": ["S", "N", "LP"],
                        "RP": ["O", "RP", "E"],
                        "S": ["RP", "O", "E"],
                        "O": ["LP", "S", "N"],
                        "N": ["LP", "S", "N"],
                        "E": []}
        self.previous: str = ""
        self.expected: list[str] = []

        self.parse()
        self.table.set_size()
        self.table.remove_whitespace()
        self.table.populate_statements()

    # Gets the current character in the current entry
    def current(self) -> str:
        return self.table.entries[self.entry][self.ptr]

    # Gets the next character in the current entry, but returns an $error string if at the end of the entry
    def next(self) -> str:
        if self.ptr+1 < self.eoe:
            return self.table.entries[self.entry][self.ptr + 1]
        return "$error"

    # Gets the current expression index at the current scope or shifted from the current scope
    def expression(self, shift=0) -> int:
        return self.ec[self.scope + shift]

    # Gets a substring of the current entry
    def inp_substring(self, start: int) -> str:
        return self.table.entries[self.entry][start:self.ptr + 1]

    # Prevents errors with indexing, and increments the scope
    def increase_scope(self):
        if self.scope+1 > len(self.table.ast[self.entry])-1:
            self.table.ast[self.entry].append([[]])
            self.ec.append(0)
        self.scope += 1

    # Again, this prevents indexing errors
    def ensure_sufficient_ec(self):
        if self.expression()+1 > len(self.table.ast[self.entry][self.scope]):
            self.table.ast[self.entry][self.scope].append([])

    def append_to_parsed(self, expression: str, shift=0):
        self.table.ast[self.entry][self.scope + shift][self.expression(shift)].append(expression)

    # Logs a reference to an expression at a higher scope
    def log_reference(self):
        expression_reference = f"${self.scope}.{self.expression()}"
        self.append_to_parsed(expression_reference, -1)

    # A ")" cannot come before a "(" because it makes no sense
    def check_scope_overflow(self):
        if self.scope < 1:
            raise SyntaxError("scope cannot be negative, i.e. no \")\" before \"(\"")

    # Catching bad operators that can pass by the parser
    def check_bad_operators(self, at):
        if self.inp_substring(at) in ["&!", "&|", "&+", "|!", "|&", "|+", "+!", "+&", "+|"]:
            raise SyntaxError("invalid operator")

    # All error handling based on expected tokens becoming unmet
    def handle_error(self, current):
        token_to_term = {"O": "operator", "N": "negation", "LP": "left parenthesis", "RP": "right parenthesis"}

        if self.previous in ["O", "N"] and current == "RP":
            raise SyntaxError("cannot end an expression with " + token_to_term[self.previous])
        elif self.previous == "LP" and current == "RP":
            raise SyntaxError("empty expression, i.e. \"()\"")
        elif self.previous == "LP" and current == "O":
            raise SyntaxError("cannot begin an expression with an operator")
        elif self.previous in ["RP", "S"] and current in ["LP", "S", "N"]:
            raise SyntaxError("must have an operator between expressions")
        elif self.previous == "O" == current:
            raise SyntaxError("cannot use consecutive operators")
        elif self.previous == "N" and current == "O":
            raise SyntaxError("cannot negate operator")
        elif self.previous == "B" and current in ["RP", "O"]:
            raise SyntaxError("cannot begin entry with " + token_to_term[current])
        elif current == "E":
            raise SyntaxError("cannot end entry with " + token_to_term[self.previous])

    def check_expected(self, current: str):
        if current not in self.expected:
            self.handle_error(current)
        else:
            self.previous = current
            self.expected = self.grammar[current]

    def parse(self):
        while self.entry+1 < self.num_entries:
            self.entry += 1
            self.table.ast.append([[[]]])
            self.eoe = len(self.table.entries[self.entry])
            self.ptr = 0
            self.scope = 0
            self.ec = [0]
            self.previous = "B"
            self.expected = self.grammar[self.previous]

            while self.ptr < self.eoe:
                if self.current() == "(":
                    self.check_expected("LP")
                    self.increase_scope()
                    self.log_reference()
                elif self.current() == ")":
                    self.check_expected("RP")
                    self.check_scope_overflow()
                    self.ec[self.scope] += 1
                    self.scope -= 1
                elif self.current().isalpha():
                    self.check_expected("S")
                    start = self.ptr
                    while self.next().isalpha():
                        self.ptr += 1
                    if self.inp_substring(start) not in self.table.statements:
                        self.table.map_statements[self.inp_substring(start)] = []
                        self.table.statements.append(self.inp_substring(start))
                    self.ensure_sufficient_ec()
                    self.append_to_parsed(self.inp_substring(start))
                elif self.current() in self.table.OPS:
                    if self.next() in self.table.OPS:
                        self.ptr += 1
                        self.check_bad_operators(self.ptr-1)
                        if self.inp_substring(self.ptr-1) == "!!":
                            self.check_expected("N")
                        else:
                            self.check_expected("O")
                        self.ensure_sufficient_ec()
                        self.append_to_parsed(self.inp_substring(self.ptr-1))
                    else:
                        raise SyntaxError("logical operators must consist of 2 symbols")
                elif self.current() in self.table.BIN:
                    self.check_expected("S")
                    self.ensure_sufficient_ec()
                    self.append_to_parsed(self.current())
                elif self.current() in self.table.WHITESPACE:
                    while self.next() in self.table.WHITESPACE:
                        self.ptr += 1
                else:
                    raise SyntaxError("unrecognized symbol")
                self.ptr += 1

            self.check_expected("E")
            if self.scope != 0:
                raise SyntaxError("need closing parenthesis \")\"")


class Interpreter:
    def __init__(self, table_input: Table):
        self.table = table_input

        self.priority = ["!&", "!|", "!+", "&&", "||", "++"]
        self.priority_ptr = 0
        self.expr_ptr = 0

        self.stack: list[list[int]] = []
        self.memory = {}
        self.memory_ptr = -1

        self.interpret()
        self.push_entries_to_map()

    def push_to_stack(self, entry, scope, expr, term):
        value = self.table.ast[entry][scope][expr][term]

        # Pulls references from higher scopes when applicable
        if value[0] == "$":
            t = value[1:].split(".")
            value = self.table.ast[entry][int(t[0])][int(t[1])][0]
            self.table.ast[entry][scope][expr][term] = value

        # Evaluates the term given and appends to the stack accordingly
        if value in self.table.statements:
            self.stack.append(self.table.map_statements[value])
        elif value[0] == "#":
            self.stack.append(self.memory[value])
        elif value == "0":
            self.stack.append([0] * self.table.size)
        elif value == "1":
            self.stack.append([1] * self.table.size)

    def flush_stack(self):
        self.stack = []

    # Stack references look like "#1", "#27", etc.
    def create_stack_reference(self) -> str:
        self.memory_ptr += 1
        return "#" + str(self.memory_ptr)

    """
    The following seven functions actually process the logical operations on values pushed to the stack
    """
    def not_of_stack(self, *args) -> list[int]:
        if len(args) == 1:
            return [1 - i for i in args[0]]
        elif len(args) == 0:
            return [1 - i for i in self.stack[0]]

    def and_of_stack(self) -> list[int]:
        return [self.stack[0][i] & self.stack[1][i] for i in range(self.table.size)]

    def or_of_stack(self) -> list[int]:
        return [self.stack[0][i] | self.stack[1][i] for i in range(self.table.size)]

    def xor_of_stack(self) -> list[int]:
        return [self.stack[0][i] ^ self.stack[1][i] for i in range(self.table.size)]

    def not_and_of_stack(self) -> list[int]:
        return self.not_of_stack(self.and_of_stack())

    def not_or_of_stack(self) -> list[int]:
        return self.not_of_stack(self.or_of_stack())

    def not_xor_of_stack(self) -> list[int]:
        return self.not_of_stack(self.xor_of_stack())

    # Negation operations involve one operand, instead of two, so it is treated separately
    def push_not_of(self, entry, scope, expr):
        reference = self.create_stack_reference()
        self.push_to_stack(entry, scope, expr, self.expr_ptr+1)

        self.memory[reference] = self.not_of_stack()

        self.flush_stack()
        self.table.ast[entry][scope][expr].pop(self.expr_ptr+1)

        self.table.ast[entry][scope][expr][self.expr_ptr] = reference

    # Operations between two operands executed here. The expression pointer points to the operator,
    # so the operands are the -1 and +1 shifts
    def push_operation_of(self, entry, scope, expr):
        reference = self.create_stack_reference()
        self.push_to_stack(entry, scope, expr, self.expr_ptr-1)
        self.push_to_stack(entry, scope, expr, self.expr_ptr+1)

        if self.table.ast[entry][scope][expr][self.expr_ptr] == "!&":
            self.memory[reference] = self.not_and_of_stack()
        elif self.table.ast[entry][scope][expr][self.expr_ptr] == "!|":
            self.memory[reference] = self.not_or_of_stack()
        elif self.table.ast[entry][scope][expr][self.expr_ptr] == "!+":
            self.memory[reference] = self.not_xor_of_stack()
        elif self.table.ast[entry][scope][expr][self.expr_ptr] == "&&":
            self.memory[reference] = self.and_of_stack()
        elif self.table.ast[entry][scope][expr][self.expr_ptr] == "||":
            self.memory[reference] = self.or_of_stack()
        elif self.table.ast[entry][scope][expr][self.expr_ptr] == "++":
            self.memory[reference] = self.xor_of_stack()

        self.flush_stack()
        self.table.ast[entry][scope][expr].pop(self.expr_ptr+1)
        self.table.ast[entry][scope][expr].pop(self.expr_ptr)

        self.table.ast[entry][scope][expr][self.expr_ptr-1] = reference

    # The zeroth scope might have no operators, like in "0" or "p" or "(f&&g)", which can cause errors
    # since the entry result comes from the ast[entry][0][0][0] string and expects it in memory reference form "#5".
    # This function forces it into the correct form.
    def push_unhandled_statement(self, entry):
        if self.table.ast[entry][0][0][0][0] != "#":
            reference = self.create_stack_reference()
            self.push_to_stack(entry, 0, 0, 0)

            self.memory[reference] = self.stack[0]

            self.flush_stack()

            self.table.ast[entry][0][0][0] = reference

    def interpret(self):
        # Iterates through the ith entry
        for i in range(len(self.table.ast)):
            # Iterates through the jth scope in reverse order
            for j in range(len(self.table.ast[i])-1, -1, -1):
                # Iterates through the kth expression
                for k in range(len(self.table.ast[i][j])):
                    self.expr_ptr = 0
                    self.priority_ptr = 0

                    # Handles negations separately
                    while "!!" in self.table.ast[i][j][k]:
                        if self.table.ast[i][j][k][self.expr_ptr] == "!!":
                            self.push_not_of(i, j, k)
                        else:
                            self.expr_ptr += 1

                    # Iterates until an expression is reduced to its result
                    while len(self.table.ast[i][j][k]) != 1:
                        self.expr_ptr = 0
                        while self.priority[self.priority_ptr] in self.table.ast[i][j][k]:
                            if self.table.ast[i][j][k][self.expr_ptr] == self.priority[self.priority_ptr]:
                                self.push_operation_of(i, j, k)
                            else:
                                self.expr_ptr += 1
                        self.priority_ptr += 1

            self.push_unhandled_statement(i)

    # The penultimate population of the map_entries dictionary
    def push_entries_to_map(self):
        iter_entries = iter(self.table.entries)
        for entry in self.table.ast:
            self.table.map_entries[next(iter_entries)] = self.memory[entry[0][0][0]]


def print_instructions():
    print("Enter truth table entries below, separating entries with a semicolon(;).\n"
          "All statements should be alphabetic variables.\n"
          "Syntax:\n"
          "\t&& -> and\n"
          "\t|| -> or\n"
          "\t++ -> xor\n"
          "\t!! -> not\n"
          "\t!& -> not and\n"
          "\t!| -> not or\n"
          "\t!+ -> not xor\n"
          "\t0  -> false\n"
          "\t1  -> true\n")


if __name__ == "__main__":
    print_instructions()
    table = Table(input("Enter here: "))
    parser = Parser(table)
    interpreter = Interpreter(table)
    table.generate()
    print(table)
