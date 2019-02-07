# CALCULATOR.py
#
# A handy library to parse and then executed formulas.
# The library supports:
#  - plus and min
#  - times and divide
#  - brackets
#  - declaration of variables as numbers using mapping at calculation time
#  - declaration of variables as other variables (at calculation time)
#  - operator-less formulas (e.g. '[x]' or '5')
#  - Formulas with sign operators ('+1', '-1')


class Formula ():
    def __init__(self, val1=0, op="+", val2=0, verbose=True):
        self.val1 = val1
        self.val2 = val2
        self.op = op
        self.verbose = verbose

    def __str__ (self):
        return("(" + str(self.val1) + self.op + str(self.val2) + ")")

    # Calculate the formula
    def calc (self, map = {}):
        while type(self.val1) == str:
            if self.val1 not in map:
                if self.verbose: print("ERR: " + self.val1 + " not declared (interpreting as 0)")
                return 0
            self.val1 = map[self.val1]
        while type(self.val2) == str:
            if self.val2 not in map:
                if self.verbose: print("ERR: " + self.val2 + " not declared (interpreting as 0)")
                return 0
            self.val2 = map[self.val2]
        if type(self.val1) != int:
            self.val1 = self.val1.calc(map)
        if type(self.val2) != int:
            self.val2 = self.val2.calc(map)
        if self.op == "+":
            return self.val1 + self.val2
        elif self.op == "-":
            return self.val1 - self.val2
        elif self.op == "*":
            return self.val1 * self.val2
        elif self.op == "/":
            return self.val1 / self.val2

class Value (Formula):
    def __init__(self, val, verbose = True):
        super().__init__(val, "+", 0, verbose)

    def __str__(self):
        return str(self.val1)

    def calc (self, map = {}):
        while type(self.val1) == str:
            if self.val1 not in map:
                if self.verbose: print("ERR: " + self.val1 + " not declared (interpreting as 0)")
                return 0
            self.val1 = map[self.val1]
        return self.val1

# Tools
def is_int (s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def has_operator (s, operators):
    for ops in operators:
        for op in ops:
            if op in s:
                return True
    return False


def parse (s, verbose=True):
    if len(s) == 0:
        if verbose: print("Empty value found: interpreting as '0'")
        s = "0"
    value = ""
    disabled = 0
    operators = [[ '+', '-' ], [ '*', '/' ]]

    s = s.replace(' ', '')
    if not has_operator(s, operators) and s[0] == "[" and s[-1] == "]":
        return Value(s[1:-1], verbose=verbose)
    if s[0] == "(" and s[-1] == ")": s = s[1:-1]
    if is_int(s): return Value(int(s), verbose=verbose)

    # Pass in steps, making the less important operators go first
    for ops in operators:
        for i in range(len(s) - 1, -1, -1):
            c = s[i]
            if c == "(":
                disabled += 1
            elif c == ")":
                disabled -= 1
            if disabled == 0:
                if c in ops:
                    # Done, formulize
                    return Formula(parse(s[:i]), c, parse(s[i + 1:]), verbose=verbose)
                else:
                    value += c

if __name__ == "__main__":
    definitions = {}
    while True:
        print("Definitions:")
        for var in definitions:
            print("   " + var + " = " + str(definitions[var]))
        print("Use '[x]' to use x")
        print("------------------")
        print("To declare a variable, type (e.g.): '\\def: x = 5'")
        print("To exit, type '\\exit'")
        print("Otherwise, enter the string that is to be calculated:")
        s = input()
        if s[:5] == "\\def:":
            s.replace(' ', '')
            s = s[5:]
            # split on the =
            splitted = s.split("=")
            if is_int(splitted[1]): splitted[1] = int(splitted[1])
            definitions[splitted[0]] = splitted[1]
        elif s[:5] == "\\exit":
            break
        else:
            form = parse(s)
            print("Formula interpreted as: " + str(form))
            # Calculate
            print("Result: " + str(form.calc(definitions)))
        print('\n')
