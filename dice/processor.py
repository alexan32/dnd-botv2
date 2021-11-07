import d20
from discord.ext import commands


def get(directory, path, alt="0"):
    tree = directory.copy()
    stack = path.split("/")
    try:
        for key in stack:
            tree = tree[key]
    except Exception as e:
        return [alt]
    return [tree]


def bonus(directory, key, alt="0"):
    print(f"bonus: {directory['player']['bonus']}")
    try:
        return [directory["player"]["bonus"][key]]
    except:
        return [alt]


def peek(parseString, index):
    try:
        return parseString[index + 1]
    except:
        return ''


class DiceProcessorError(commands.CommandError):

    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)


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


class DiceProcessor:

    def __init__(self, crit="**", critfail="*", dropped="~"):
        self.stringifier = CustomStringifier(crit, critfail, dropped)
        self.functions = {
            "get": get,
            "bonus": bonus
        }
        self.acceptedTokens = ['+', '-', '*', '/', '(', ')', ',', 'd'] + list(self.functions.keys())


    def processString(self, input, directory):
        nameSpace = directory["player"]["rolls"]
        diceString = nameSpace[input] if input in nameSpace.keys() else input
        tokens = self.tokenize(diceString)


    def tokenize(self, parseString):
        parseString = ' '.join(parseString.split()).lower()
        tokens = []
        index = 0
        token = ''

        while True:
            current = parseString[index]
            _next = peek(parseString, index)
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
                    if not _next.isnumeric():
                        tokens.append(token)
                        token = ''
                    else:
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
        

if __name__ == "__main__":
    
    directory = {
        "player": {
            "rolls": {
                "acrobatics": "1d20 + dex + bonus(acrobatics)",
                "prof": "2",
                "dex": "3"
            }, 
            "bonus": {
                "acrobatics": "0"
            }
        }
    }

    processor = DiceProcessor()

    print(processor.tokenize("1d20 + 0 + 5 / 2"))