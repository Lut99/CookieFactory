# ADVANCED PARSER.py
#
# Parses a file in a clever way.
# The file consists of values, each indicated by the value's name, followed
#   by brackets () for the variable's name. Then, the statement is followed by
#   a {, indicating that there will be values to come. Using sort of recursion,
#   the app will then parse the values to come.

# Constants
COMMENT_BEGIN = '/*'
COMMENT_END = '*/'

# Declare the errors
class FileParseException (Exception):
    pass
class BracketException (FileParseException):
    pass
class UnknownDataTypeException (FileParseException):
    pass
class DataTypeValueException (FileParseException):
    pass

# Declare the type class
class DataType ():
    def __init__(self, keyword, parser):
        self.keyword = keyword
        self.parse = parser
# Declare the Buffer class
class Buffer ():
    # Buffer error
    class BufferOverflowException (Exception):
        pass

    def __init__(self, size=-1):
        self.size = size
        self.__buffer = ""
        self.brackets = 0
        self.curly_brackets = 0
        self.quotes = False
        self.apostrofes = False

    # Functions to add text to the buffer
    def prepend (self, text):
        if self.size > -1 and len(self.__buffer) + len(text) > self.size:
            raise Buffer.BufferOverflowException
        self.__buffer = text + self.__buffer
    def inject (self, text, pos):
        if self.size > -1 and len(self.__buffer) + len(text) > self.size:
            raise Buffer.BufferOverflowException
        self.__buffer = self.__buffer[:pos] + text + self.__buffer[pos:]
    def append (self, text):
        if self.size > -1 and len(self.__buffer) + len(text) > self.size:
            raise Buffer.BufferOverflowException
        self.__buffer += text

    # Functions to remove text from the buffer
    def remove_first (self, count):
        self.__buffer = self.__buffer[count:]
    def remove_range (self, start, stop):
        self.__buffer = self.__buffer[:start] + self.__buffer[stop + 1:]
    def remove_last (self, count):
        self.__buffer = self.__buffer[:-count]

    # Clears the buffer
    def flush (self):
        self.__buffer = ""

    # Returns the buffer contents
    def get (self):
        return self.__buffer

    # Allows for direct indexing
    def __getitem__(self, key):
        return self.__buffer[key]

    # Functions directly related to the parsing
    # Checks whether we somehow are in any literal mode
    def is_literal (self):
        return self.brackets > 0 or self.curly_brackets > 0 or self.quotes or self.apostrofes

# The standard DataType parsers
def string_parser (text, DataTypes):
    # Simply return the text
    return text
def int_parser (text, DataTypes):
    # Try to convert to int
    try:
        return int(text)
    except ValueError:
        raise DataTypeValueException("Could not parse '{}' as int: needs to be a whole number".format(text))
def uint_parser (text, DataTypes):
    # Convert to int
    n = int_parser(text, DataTypes)
    if n < 0:
        raise DataTypeValueException("Could not parse '{}' as uint: cannot be negative".format(text))
def float_parser (text, DataTypes):
    # Try to convert to float
    try:
        return float(text)
    except ValueError:
        raise DataTypeValueException("Could not parse '{}' as float: needs to be a number".format(text))
def bool_parser (text, DataTypes):
    # If not true (or 1) or false (or 0), return
    text = text.lower()
    if text == "1" or text == "true":
        return True
    elif text == "0" or text == "false":
        return False
    else:
        raise DataTypeValueException("Could not parse '{}' as bool: needs to be '1' or 'true' for True, '0' or 'false' for False".format(text))
def dict_parser (text, DataTypes):
    # Fetch only the new types
    custom = []
    for t in DataTypes:
        if t not in DATATYPES:
            custom.append(t)
    # Use recursion to parse this dict
    return parse(text, parseString=True, customDataTypes=custom)

String = DataType('string', string_parser)
Int = DataType('int', int_parser)
UInt = DataType('uint', uint_parser)
Float = DataType('float',float_parser)
Bool = DataType('bool',bool_parser)
List = DataType('list',dict_parser)

DATATYPES = [
    # String
    String,
    Int,
    UInt,
    Float,
    Bool,
    List
]

def parse (filepath, parseString=False, customDataTypes=[]):
    # Next, add the custom ones
    for t in customDataTypes:
        check = True
        for std_t in DATATYPES:
            if t.keyword == std_t.keyword:
                check = False
                print("WARNING: Custom DataType with standard keyword '{}' found, ignoring".format(t.keyword))
                break
        if check:
            DATATYPES.append(t)
        
    # If not parsing the filepath as string, read it first
    data = filepath
    if not parseString:
        with open(filepath, "r") as f:
            data = f.read()
    # Pre-parse: remove all newlines
    data = data.replace("\n", "")
    # Buffer object
    buf = Buffer()
    # Now parse:
    #  - remove all spaces not directly in '', "" or ()
    #  - remove all comments (starting with /* and ending with */)
    #  - Parse until encountered bracket or curly bracket until the matching
    #  -   end is found
    i = 0
    comments = False
    var_type = ""
    var_name = ""
    parsed_dict = {}
    while i < len(data):
        c = data[i]
        if i < len(data) - 1 and not comments and c == "/" and data[i + 1] == "*":
            # Engage comment mode
            comments = True
            i += 1
        elif i < len(data) - 1 and comments and c == "*" and data[i + 1] == "/":
            # Disengage
            comments = False
            i += 1
        elif not comments:
            # Check for literals (' or ")
            if (not buf.apostrofes and buf.brackets == 0 and buf.curly_brackets == 0) and c == "'" and (i == 0 or data[i - 1] != "\\"):
                buf.apostrofes = not bug.apostrofes
            elif (not buf.apostrofes and buf.brackets == 0 and buf.curly_brackets == 0) and c == '"' and (i == 0 or data[i - 1] != "\\"):
                buf.quotes = not buf.quotes
            elif not buf.apostrofes and not buf.quotes:
                # Check for bracket or curly bracket start
                if buf.curly_brackets == 0 and c == "(":
                    if buf.brackets == 0:
                        if len(buf.get()) == 0:
                            raise FileParseException("Expected type of variable, got value: '{}'".format(data[i - 5:i + 6]))
                        # Save the type
                        var_type = buf.get()
                        check = False
                        for t in DATATYPES:
                            if t.keyword == var_type:
                                check = True
                                break
                        if not check:
                            raise UnknownDataTypeException("Unknown Datatype encountered: '{}'".format(var_type))
                        # Flush the buffer
                        buf.flush()
                    else:
                        buf.append(c)
                    buf.brackets += 1
                elif buf.curly_brackets == 0 and c == ")":
                    if buf.brackets == 0:
                        raise BracketException("Stray ')' discovered: '{}'".format(data[i - 5:i + 6]))
                    buf.brackets -= 1
                    if buf.brackets == 0:
                        # Simply save the name
                        var_name = buf.get()
                        if var_name in parsed_dict:
                            print("WARNING: Variable with name '{}' already declared, overwriting".format(var_name))
                    else:
                        # Add the bracket to the buffer
                        buf.append(c)
                elif buf.brackets == 0 and c == "{":
                    if buf.curly_brackets == 0:
                        if var_name == "":
                            raise FileParseException("Expected name of variable, got value: '{}'".format(data[i - 5:i + 6]))
                        # Flush the buffer
                        buf.flush()
                    else:
                        buf.append(c)
                    buf.curly_brackets += 1
                elif buf.brackets == 0 and c == "}":
                    if buf.curly_brackets == 0:
                        raise BracketException("Stray '}' discovered: '" + data[i - 5:i + 6] + "'")
                    buf.curly_brackets -= 1
                    if buf.curly_brackets == 0:
                        # We've got a load new stuff, parse the buffer according to the type
                        for t in DATATYPES:
                            if t.keyword == var_type:
                                parsed_dict[var_name] = t.parse(buf.get(), DATATYPES)
                                # Reset the var_name and var_type
                                var_name == ""
                                var_type == ""
                                break
                        # Clear buffer
                        buf.flush()
                    else:
                        # Add the bracket to the buffer
                        buf.append(c)
                elif c != "\\" or (i > 0 and data[i - 1] == "\\"):
                    # Now add it to the buffer (unless '\', unless '\\')
                    if c == ' ' and buf.brackets == 0 and buf.curly_brackets == 0:
                        c = ""
                    buf.append(c)
            else:
                if c != "\\" or (i > 0 and data[i - 1] == "\\"):
                    buf.append(c)
        i += 1
    if buf.curly_brackets != 0:
        raise FileParseException("EOF while searching for '}'")
    if buf.brackets != 0:
        raise FileParseException("EOF while searching for ')'")
    return parsed_dict

# Test
if __name__ == "__main__":
    print(parse("Factory/cookie_factory.recipes", customDataTypes=[ DataType('recipe', dict_parser) ]))
