import d20
from discord.ext import commands

def insert(_list, _input, index):
    _input.reverse()
    for x in _input:
        _list.insert(index, x)
    return _list


def replace_segment(_list, start, end, _input):
    del _list[start:end]
    _list = insert(_list, _input, start)
    return _list


class DiceProcessorError(commands.CommandError):

    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)


class DiceProcessor:

    def __init__(self, functions={}, crit='**', critfail='*', dropped='~'):
        self.strigifier = CustomStringifier(crit, critfail, dropped)
        self.functions = functions
        self.acceptedTokens = ['+', '-', '*', '/', '(', ')', ',', 'd'] + list(self.functions.keys())


    def processString(self, diceString, nameSpace={}):
        print(self.functions)
        diceString = nameSpace[diceString] if diceString in nameSpace.keys() else diceString
        tokens = self.tokenize(diceString)
        if len(nameSpace.keys()) > 0:
            tokens = self.populateVariables(tokens, nameSpace)
        tokens = self.performFunctions(tokens)
        processedString = ''.join(tokens)
        try:
            return d20.roll(processedString, stringifier=self.strigifier)
        except d20.errors.RollSyntaxError as e:
            print(e)
            raise DiceProcessorError(f"Unexpected value in '{processedString}'")


    def tokenize(self, parseString):
        parseString = ' '.join(parseString.split()).lower()
        tokens = []
        index = 0
        token = ''

        while True:
            current = parseString[index]
            _next = self.peek(parseString, index)
            token += current

            if current.isalpha():
                if current == 'd' and not _next.isalpha():
                    tokens.append(token)
                    token = ''
                elif not _next.isalpha():
                    tokens.append(token)
                    token = ''

            elif current.isnumeric():
                if current == '0' and len(token) == 1:
                    token = ''
                elif not _next.isnumeric():
                    tokens.append(token)
                    token = ''

            elif current in self.acceptedTokens:
                tokens.append(token)
                token = ''

            elif current.isspace():
                tokens.append(token)
                token = ''

            else:
                raise DiceProcessorError(f'"{current}" is not an accepted character.')

            index += 1
            if index == len(parseString):
                break
        
        return tokens


    def populateVariables(self, tokens, nameSpace={}):
        index = 0
        while index < len(tokens):
            token = tokens[index]
            if token in nameSpace.keys():
                if not (token in self.functions.keys() and self.peek(tokens, index) == '('):
                    newTokens = self.tokenize(nameSpace[token])
                    tokens = tokens[:index] + newTokens + tokens[index+1:]
            index += 1
        return tokens


    def performFunctions(self, tokens):
        index = 0
        while index < len(tokens):
            token = tokens[index]
            if token in self.functions.keys() and self.peek(tokens, index) == '(':
                print(f"Function! {token}")
                func = token
                args = []
                arg = ''
                index2 = index + 1
                while True:
                    token = tokens[index2]
                    if token == '(':
                        pass
                    elif token == ',' and arg != '':
                        args.append(arg)
                        arg = ''
                    elif token == ')':
                        if arg != '':
                            args.append(arg)
                        index2 += 1
                        break
                    else:
                        arg += token
                    index2 += 1
                print(f"FUNCTION: {func} ARGS: {args}")
                output = self.functions[func](*args)
                print(f"FUNCTION: {func} OUTPUT: {output}")
                replace_segment(tokens, index, index2, output)
            index += 1
        return tokens


    def peek(self, parseString, index):
        try:
            return parseString[index + 1]
        except:
            return ''


class CustomStringifier(d20.SimpleStringifier):

    class _MDContext:
        def __init__(self):
            self.in_dropped = False

        def reset(self):
            self.in_dropped = False

    def __init__(self, crit='**', critfail='*', dropped='~'):
        self.crit = crit
        self.critfail = critfail
        self.dropped = dropped
        self._context = self._MDContext()
        super().__init__()

    def stringify(self, the_roll):
        self._context.reset()
        return super().stringify(the_roll)

    def _stringify(self, node):
        if not node.kept and not self._context.in_dropped:
            self._context.in_dropped = True
            inside = super()._stringify(node)
            self._context.in_dropped = False
            return f"{self.dropped}{inside}{self.dropped}"
        return super()._stringify(node)

    def _str_die(self, node):
        the_rolls = []
        for val in node.values:
            inside = self._stringify(val)
            if val.number == node.size:
                inside = f"{self.crit}{inside}{self.crit}"
            elif val.number == 1:
                inside = f"{self.critfail}{inside}{self.critfail}"
            the_rolls.append(inside)
        return ', '.join(the_rolls)

    def _str_expression(self, node):
        return f"{self._stringify(node.roll)} = {int(node.total)}"


if __name__ == '__main__':
    nameSpace = {
        "str": "-1",
        "dex": "4",
        "con": "1",
        "wis": "2",
        "int": "0",
        "char": "5",
        "prof": "3",
        "stealth": "1d20 + dex + prof",
        "unarmed": "1d20 + prof + min(str, dex)"
    }

    def hit():
        return ['17']

    funcs = {
        'hit': hit
    }

    processor = DiceProcessor(funcs)
    result = processor.processString("1d20 - hlkj", nameSpace)
    print(result)
    # for x in range(100):
    #     result = processor.processString("1d20", nameSpace)
    #     print(result)
