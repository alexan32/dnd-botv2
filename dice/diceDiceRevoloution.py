import re
from uuid import uuid4
from random import randint

# UTIL===============================================================

class MissingVariableException(Exception):
    def __init__(self, variables):
        self.message = f"Failed to populate the following variables: {variables}"

class DepthExceededException(Exception):
    def __init__(self):
        self.message = "Depth exceeded while performing variable replacement."

def sanitize(expression: str):
    return "".join(expression.split()).lower()

def tokensAsString(tokens: list):
    return "".join(x[1] for x in tokens)

def print_tree(node):
    stack = [(node, '')]
    while stack:
        current_node, indent = stack.pop()
        print(indent + current_node.value)
        stack.extend((child, indent + '  ') for child in current_node.children)

# TOKENIZER  ======================================================

def tokenize(expression):
    tokenSpecification = [
        ('NUMBER',  r'(?<![d\d])\d+(?![d\d])(\.\d*)?'),                     # Integer or decimal number
        ('ADD',     r'\+'),                                                 # Addition operator
        ('SUB',     r'-'),                                                  # Subtraction operator
        ('MUL',     r'\*'),                                                 # Multiplication operator
        ('DIV',     r'/'),                                                  # Division operator
        ('POWER',   r'\^'),                                                 # Exponentiation operator
        ('LPAREN',  r'\('),                                                 # Left parenthesis
        ('RPAREN',  r'\)'),                                                 # Right parenthesis
        ('D',       r'\d+d\d+[A-Za-z0-9]*'),                                # Dice expression
        ('VAR',     r'(?<!\d)d?(?![\d])[a-zA-Z]+|[ace-zA-Z]+')              # Variable token
    ]
    tokenRegex = '|'.join('(?P<%s>%s)' % pair for pair in tokenSpecification)
    # Use regex to match tokens in the expression string
    return [(matchObject.lastgroup, matchObject.group()) for matchObject in re.finditer(tokenRegex, expression)]

def replaceVariables(tokens:list, variables:dict):
    i = 0
    replacements = 0
    missingVars = []
    while i < len(tokens):
        if tokens[i][0] == 'VAR':
            if tokens[i][1] in variables:
                if replacements > 30:
                    raise DepthExceededException()
                newTokens = tokenize(sanitize(variables[tokens[i][1]])) 
                del tokens[i]
                tokens[i:i] = [('LPAREN', '(')] + newTokens + [('RPAREN', ')')]
                replacements += 1
            else:
                missingVars.append(tokens[i])
            
        i += 1
    return missingVars, tokens


# INTERPRETER  ======================================================

def evaluateTree(root, advantage=""):
    stack = []
    explored = []
    currentNode = root

    while currentNode != None:

        explored.append(currentNode.id)

        # get children of current node
        lchild = None
        rchild = None
        if len(currentNode.children) >= 1:
            lchild = currentNode.children[0]
        if len(currentNode.children) == 2:
            rchild = currentNode.children[1]

        # move to children if they have not yet been visited
        if lchild and lchild.id not in explored:
            currentNode = lchild
        elif rchild and rchild.id not in explored:
            currentNode = rchild
        
        # add value to stack. check for and perform operation. move to parent node.
        else:
            
            if currentNode.type == 'D':
                val = currentNode.value

                # use regex to split dice expression into operands and modifiers
                matchObject = re.match(r'(\d+)d(\d+)([A-Za-z0-9]*)',val)
                lop = matchObject.group(1)
                rop = matchObject.group(2)

                # evaluate dice expression
                dice, info = diceRoll(int(lop), int(rop), matchObject.group(3), advantage=advantage)
                currentNode.data["dice"] = dice
                currentNode.data["info"] = info
                total = sum(dice)

                # print(f"diceroll: {lop}D{rop} {dice} = {total}")
                stack.append(total)

            elif currentNode.type in ('ADD', 'SUB', 'MUL', 'DIV'):
                operator = currentNode.value
                rop = stack.pop(-1)
                lop = stack.pop(-1)
                # print(f"{lop} {operator} {rop}")
                result = eval(f"{lop} {operator} {rop}")
                stack.append(result)

            else:
                stack.append(currentNode.value)

            if currentNode.parent is None:
                if type(stack[0]) is float:
                    total = float('{0:.2f}'.format(stack[0]))
                    stack[0] = total
                currentNode.data["evaluation"] = stack
            currentNode = currentNode.parent

    return stack[0]


def treeToExpression(root):
    currentNode = root
    explored = []
    expression = ""

    while currentNode != None:

        # get children of current node
        lchild = None
        rchild = None
        if len(currentNode.children) >= 1:
            lchild = currentNode.children[0]
        if len(currentNode.children) == 2:
            rchild = currentNode.children[1]

        # 1. move to left child
        if lchild and lchild.id not in explored:
            currentNode = lchild
        
        # 2. if lc already explored, explore self
        elif currentNode.id not in explored:
            explored.append(currentNode.id)
            
            # update expression based on current node
            expression += currentNode.value
            if currentNode.type == 'D' and 'dice' in currentNode.data:
                expression += f"{currentNode.data['info']}({sum(currentNode.data['dice'])})"
        
        # 3. if lc and self explored, move to rc
        elif rchild and rchild.id not in explored:
            currentNode = rchild

        # 4. all children explored, move to parent
        else:
            
            # if tree already evaluated, add evaluation to expression
            if currentNode.parent is None and "evaluation" in currentNode.data:
                expression += f" = {currentNode.data['evaluation'][0]}"
            
            # move to parent
            currentNode = currentNode.parent

    for x in ["+", '-', '*', '/']:
        expression = f" {x} ".join(expression.split(x))

    return expression



# OPERATORS =========================================================

# mi
def minimum(rop:int, rolls:list, minimum:int):
    for i in range(len(rolls)):
        roll = rolls[i]
        if roll < minimum:
            while roll < minimum:
                roll = diceRoll(1, rop)[0][0]
            rolls[i] = roll
    return rolls, []

# ma
def maximum(rop:int, rolls:list, maximum:int):
    for i in range(len(rolls)):
        roll = rolls[i]
        if roll > maximum:
            while roll > maximum:
                roll = diceRoll(1, rop)[0][0]
            rolls[i] = roll
    return rolls, []

# rr
def reroll(rop:int, rolls:list, integer:int):
    dropped = []
    for i in range(len(rolls)):
        roll = rolls[i]
        if roll == integer:
            while roll == integer:
                dropped.append(roll)
                roll = diceRoll(1, rop)[0][0]
            rolls[i] = roll
    return rolls, dropped

# ro
def rerollOnce(rop:int, rolls:list, integer:int):
    dropped = []
    for i in range(len(rolls)):
        roll = rolls[i]
        if roll == integer:
            dropped.append(roll)
            rolls[i] = diceRoll(1, rop)[0][0]
    return rolls, dropped

# e
def explode(rop:int, rolls:list, integer:int):
    for roll in rolls:
        if roll == integer:
            rolls.append(diceRoll(1, rop)[0][0])
    return rolls

# k
def keep(rolls:list, selector:str, integer:int):
    if selector not in ('l', 'h', '<', '>'):
        raise TypeError(f"Invalid selector \"{selector}\". Valid selctors are l, h, <, and >.")
    kept = selectors[selector](rolls, integer)
    dropped = list(rolls)
    for x in kept:
        dropped.remove(x)
    return kept, dropped

# p
def drop(rolls:list, selector:str, integer:int):
    toDrop, toKeep = keep(rolls, selector, integer)
    return toKeep, toDrop

# SELECTORS==========================================================

# hX
def highest(rolls:list, quantity:int):
    rolls.sort()
    return rolls[len(rolls)-quantity:]

# lX
def lowest(rolls:list, quantity:int):
    rolls.sort()
    return rolls[:quantity]

# >X
def greaterThan(rolls:list, integer:int):
    return [x for x in rolls if x > integer]
    
# <X
def lessThan(rolls:list, integer:int):
    return [x for x in rolls if x < integer]

selectors = {
    'h': highest,
    'l': lowest,
    '<': lessThan,
    '>': greaterThan
}


# lop: left operand of the 'd' operator
# rop: right operand of the 'd' operator
# modifiers: rules applied after initial dice rolls
# peekSymbol: in dice results, marks that a di rolled its highest possible value
# removedSymbol: in dice rsults, marks that a di roll was removed from the di pool
# advantage: accepted values are "a", "d", or empty string
def diceRoll(lop:int, rop:int, modifiers:str="", peekSymbol:str="!", removedSymbol:str="~", advantage:str=""):
    rolls = []
    dropped = []

    if advantage not in ("a", "d", ""):
        raise ValueError(f"Invalid \"advantage\" arg for diceRoll fuction: {advantage}. valid values are \"a\", \"d\", or empty string.")
    elif advantage == "a" and lop == 1 and rop == 20 and modifiers == "":
        lop = 2
        modifiers = "kh1"
    elif advantage == "d":
        lop = 2
        modifiers = "ph1"

    for x in range(0, lop):
        rolls.append(randint(1, rop))
    # print(f"{lop}D{rop}={rolls}")

    if modifiers:

        # check for invalid characters
        match = re.match(r'((k|p|rr|ro|e|mi|ma)(\d+|h\d+|l\d+|\<\d+|\>\d+))*', modifiers)
        if match and match[0] != modifiers:
            badCharacters = modifiers.split(match[0])
            badCharacters.remove("")
            raise SyntaxError(f"Invalid character(s) in dice modifier expression '{lop}d{rop}{modifiers}': {badCharacters}")

        # loop over operation + selector combos
        dropped = []
        for match in re.findall(r'(k|p|rr|ro|e|mi|ma)(\d+|h\d+|l\d+|\<\d+|\>\d+)', modifiers):
            op = match[0]
            removed = []
            # print(match)

            # keep selection
            if op == 'k':
                if match[1].isdigit():
                    raise SyntaxError(f"invalid selector for 'keep' operation: {match[1]}")
                rolls, removed = keep(rolls, match[1][0], int(match[1][1:]))
            
            # drop selection
            elif op == 'p':
                if match[1].isdigit():
                    raise SyntaxError(f"invalid selector for 'drop' operation: {match[1]}")
                rolls, removed = drop(rolls, match[1][0], int(match[1][1:]))
            
            # reroll on X
            elif op == 'rr':
                if not match[1].isdigit():
                    raise SyntaxError(f"invalid selector for 'reroll' operation: {match[1]}")
                rolls, removed = reroll(rop, rolls, int(match[1]))
            
            # reroll once on X or reroll once on selection
            elif op == 'ro':
                if match[1].isdigit():
                    rolls, removed = reroll(rop, rolls, int(match[1]))
                else:
                    selection = selectors[match[1][0]](rolls, int(match[1][1:]))
                    removed = []
                    for roll in selection:
                        removed.append(roll.index(roll))
                        rolls[rolls.index(roll)] = diceRoll(1, rop)[0]
            
            # explode on X
            elif op == 'e':
                if not match[1].isdigit():
                    raise SyntaxError(f"invalid selector for 'explode' operation: {match[1]}")
                rolls = explode(rop, rolls, int(match[1]))
            
            # minimum X
            elif op == 'mi':
                if not match[1].isdigit():
                    raise SyntaxError(f"invalid selector for 'minimum' operation: {match[1]}")
                rolls, removed = minimum(rop, rolls, int(match[1]))
            
            # maximum X
            elif op == 'ma':
                if not match[1].isdigit():
                    raise SyntaxError(f"invalid selector for 'maximum' operation: {match[1]}")
                rolls, removed = maximum(rop, rolls, int(match[1]))

            dropped.extend(removed)

    isMaxPipe = lambda x: f"{peekSymbol}{x}" if x == rop else str(x)
    info = [f"{removedSymbol}{x}" for x in dropped] + [isMaxPipe(x) for x in rolls]

    return rolls, info

# PARSER ============================================================

class TreeNode:
    def __init__(self, value, _type):
        self.id = str(uuid4())
        self.value = value
        self.type = _type
        self.parent = None
        self.children = []
        self.data = {}
        

class TreeGenerator():

    def __init__(self):
        self.index = 0

    def generateParseTree(self, tokens):
        self.index = 0
        root = self.parseExpression(tokens)

        if self.index < len(tokens):
            raise SyntaxError("Invalid token: {}".format(tokens[self.index][1]))

        return root


    def parseExpression(self, tokens):
        # Parse the first term
        node = self.parseTerm(tokens)

        # Continue parsing while there are addition or subtraction tokens
        while self.index < len(tokens) and tokens[self.index][0] in ('ADD', 'SUB'):
            token = tokens[self.index]
            self.index += 1
            child = self.parseTerm(tokens)
            operatorNode = TreeNode(token[1], token[0])
            node.parent = operatorNode
            child.parent = operatorNode
            operatorNode.children.append(node)
            operatorNode.children.append(child)
            node = operatorNode

        return node


    def parseTerm(self, tokens):
        # Parse the first factor
        # node = self.parse_dice(tokens)
        node = self.parseFactor(tokens)

        # Continue parsing while there are multiplication or division tokens
        while self.index < len(tokens) and tokens[self.index][0] in ('MUL', 'DIV'):
            token = tokens[self.index]
            self.index += 1
            # child = self.parse_dice(tokens)
            child = self.parseFactor(tokens) 
            operatorNode = TreeNode(token[1], token[0])
            node.parent = operatorNode
            child.parent = operatorNode
            operatorNode.children.append(node)
            operatorNode.children.append(child)
            node = operatorNode

        return node

    def parseFactor(self, tokens):
        
        # Get the current token
        token = tokens[self.index]
        self.index += 1

        if token[0] in ('NUMBER', 'VAR', 'D'):

            # insert multiplication token of num followed immediately by paren
            if self.index < len(tokens) and tokens[self.index][0] == 'LPAREN':
                tokens.insert(self.index, ('MUL', '*'))

            # Create a leaf node with the token value (number or variable)
            return TreeNode(token[1], token[0])

        elif token[0] == 'LPAREN':
            # If the token is a left parenthesis, parse the expression inside the parentheses
            node = self.parseExpression(tokens)
            # Verify that there is a matching right parenthesis
            if tokens[self.index][0] != 'RPAREN':
                raise SyntaxError("Missing closing parenthesis")
            self.index += 1

            return node
        elif token[0] == 'SUB' and self.index < len(tokens) and tokens[self.index][0] == 'NUMBER':
            # Handling negative numbers (unary minus)
            numberToken = tokens[self.index]
            self.index += 1

            # Create a negative number node
            return TreeNode('-' + numberToken[1], numberToken[0])
        else:
            raise SyntaxError("Invalid token: {}".format(token[1]))


class DiceProcessor:

    def __init__(self):
        self.generator = TreeGenerator()

    def processDiceString(self, diceString:str, variables={}, advantage=""):
        
        total = None
        expression = ""

        # Step 1: tokenization
        tokens = tokenize(diceString)
        missingVars, tokens = replaceVariables(tokens, variables)
        if len(missingVars) > 0:
            raise MissingVariableException([x[1] for x in missingVars])

        # Step 2: parsing
        root = self.generator.generateParseTree(tokens)
        
        # Step 3: interpreting
        total = evaluateTree(root, advantage)
        expression = treeToExpression(root)

        return total, expression
    

if __name__ == "__main__":
    dp = DiceProcessor()
    print(dp.processDiceString("10 / 3")[1])
    print(dp.processDiceString("1d20 + prof + dex", {"prof": "2", "dex": "3"}, advantage="")[1])
    print(dp.processDiceString("1d20 + prof + dex", {"prof": "2", "dex": "3"}, advantage="a")[1])
    print(dp.processDiceString("hit", {"hit":"1d20 + dex + prof", "prof": "2", "dex": "3"}, advantage="d")[1])