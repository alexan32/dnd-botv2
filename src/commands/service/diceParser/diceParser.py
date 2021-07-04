import math
import random

count = 0
def makeId():
    global count 
    count += 1
    return str(count)

# ---------------------------------------------------------
class Node:

    def __init__(self, _id=None):
        self.id = _id if _id != None else makeId()
        self.value = None
        self.parent = None
        self.leftChild = None
        self.rightChild = None
        self.visited = False

    def stringify(self):
        return f"id: {self.id}".ljust(15) + f"value: {self.value}".ljust(15) + f"parent: {self.parent}".ljust(20) +f"left child: {self.leftChild}".ljust(25) + f"right child: {self.rightChild}".ljust(25)

# ---------------------------------------------------------
class DiceParser:

    def __init__(self):
        self.numbers = ["0","1","2","3","4","5","6","7","8","9"]
        self.ops = ["+","-","*","/", "d"]
        self.parseTree = None
        self.rootId = None
        self.diceString = None
 

    def tokenize(self, diceString):
        diceString = "".join(diceString.lower().split())
        self.diceString = diceString
        index = 0
        currentToken = ""
        tokens = []
        isZeroAfter = False

        while index in range(len(diceString)):
            char = diceString[index]
            nextChar = self.peek(diceString, index)
            # print(f"current: {char} next: {nextChar}")
            # print(tokens)

            if not char in ["0","1","2","3","4","5","6","7","8","9","+","-","*","/", "d"] or (char == "d" and not self.charIsNumeric(nextChar)):
                currentToken += char
                if self.charIsNumeric(nextChar) or nextChar in ["+","-","*","/"] or nextChar == None:
                    tokens.append(currentToken)
                    currentToken = ""

            elif char == "d" and self.charIsNumeric(nextChar):
                isZeroAfter = False
                if index == 0:
                    tokens.append("1")
                elif diceString[index -1] not in self.numbers:
                    tokens.append("1")
                tokens.append(char)
                currentToken = ""

            elif char == '-':
                try:
                    previous = tokens[len(tokens)-1]
                except:
                    previous = None

                if self.charIsNumeric(nextChar) and previous in ['+', '-', '*', '/', None]:
                    currentToken = "-"
                else:
                    tokens.append(char)
                    currentToken = ""

            elif char in self.numbers:
                if char == "0" and self.peek(diceString, index) in self.numbers:
                    if isZeroAfter:
                        currentToken += char
                else: 
                    isZeroAfter = True
                    currentToken += char
                if self.peek(diceString, index) not in self.numbers:
                    tokens.append(currentToken)
                    currentToken = ""

            else:
                isZeroAfter = False
                tokens.append(char)
                currentToken = ""

            index += 1
        return tokens


    def isValidCharacter(self, char):
        return True if (char in self.numbers) or (char in self.ops) else False


    def peek(self, string, index):
        try:
            return string[index + 1]
        except IndexError:
            return None


    def charIsNumeric(self, char):
        if char == None:
            return False
        if char[0] == '-' and len(char) > 1:
            return char[1:].isnumeric()
        return char.isnumeric()


    def buildParseTree(self, tokens):
        self.parseTree = {}
        currentNode = Node()
        currentNodeId = currentNode.id
        self.parseTree = {currentNodeId: currentNode}

        # build parse tree
        while len(tokens) > 0:
            currentToken = tokens.pop(0)
            currentNode = self.parseTree[currentNodeId]

            if self.charIsNumeric(currentToken):
                # create child node. move to child. store value
                child = Node()
                self.parseTree[child.id] = child
                child.value = int(currentToken)
                if currentNode.leftChild == None:
                    currentNode.leftChild = child.id
                    child.parent = currentNode.id
                else:
                    currentNode.rightChild = child.id
                    child.parent = currentNode.id
                currentNodeId = child.id
            elif currentToken == "d":
                stop = self.traverse(["*", "/", "+","-"], currentNode.id)
                currentNode = self.parseTree[stop]
                if currentNode.value == None:
                    currentNode.value = currentToken
                    currentNodeId = currentNode.id
                elif currentNode.parent == None:
                    parent = Node()
                    parent.leftChild = currentNode.id
                    currentNode.parent = parent.id
                    parent.value = currentToken
                    currentNodeId = parent.id
                else:
                    newId = self.replaceMe(currentNode.id)
                    currentNode = self.parseTree[newId]
                    currentNode.value = currentToken
                    currentNodeId = newId
            elif currentToken in ["*", "/", "+", "-"]:
                stop = self.traverse(["+","-"], currentNode.id)
                currentNode = self.parseTree[stop]
                if currentNode.value == None:
                    currentNode.value = currentToken
                    currentNodeId = stop
                elif currentNode.parent == None:
                    parent = Node()
                    self.parseTree[parent.id] = parent
                    currentNode.parent = parent.id
                    parent.leftChild = currentNode.id
                    parent.value = currentToken
                    currentNodeId = parent.id
                else:
                    newId = self.replaceMe(currentNode.id)
                    currentNode = self.parseTree[newId]
                    currentNode.value = currentToken
                    currentNodeId = newId
            # input()
            # print("currentToken: " + str(currentToken))
            # print("currentNode: " + str(currentNodeId))
        # for key in parser.parseTree:
        #     print(parser.parseTree[key].stringify())

        self.rootId = self.traverse([], currentNodeId)
    

    def replaceMe(self, _id):
        child = self.parseTree[_id]
        parent = self.parseTree[child.parent]
        isLeftChild = False if parent.rightChild == child.id else True
        new = Node()
        new.parent = parent.id
        new.leftChild = child.id
        child.parent = new.id
        if isLeftChild:
            parent.leftChild = new.id
        else:
            parent.rightChild = new.id
        self.parseTree[new.id] = new
        return new.id
        
        
    def parse(self, diceString):
        print(f"parsing '{diceString}'")
        tokens = self.tokenize(diceString)
        self.buildParseTree(tokens)
        total = self.runParse()
        resultString = self.diceString + f" = {str(total)}"
        resultString = resultString.replace("+", " + ")
        resultString = resultString.replace("*", " * ")
        resultString = resultString.replace("/", " / ")
        resultString = resultString.replace("-", " - ")
        return resultString


    def runParse(self):
        stack = []
        currentNodeId = self.rootId
        parsing = True

        while parsing:
            value = None
            currentNode = self.parseTree[currentNodeId]
            if currentNode.leftChild != None and self.parseTree[currentNode.leftChild].visited != True:
                currentNodeId = currentNode.leftChild
            elif currentNode.rightChild != None and self.parseTree[currentNode.rightChild].visited != True:
                currentNodeId = currentNode.rightChild
            else:
                # add to stack. set visited to true
                value = currentNode.value
                currentNode.visited = True
                if currentNode.parent != None:
                    currentNodeId = currentNode.parent
                else:
                    parsing = False
            if value != None:
                # print(value)
                if value in self.ops:
                    # print(stack)
                    num2 = int(stack.pop())
                    num1 = int(stack.pop())
                    if value == "d":
                        result = self.roll(num1, num2)
                        asString = f"{str(num1)}d{str(num2)}"
                        resultString = asString + f"({str(result)})"
                        stack.append(result)
                        self.diceString = self.diceString.replace(asString, resultString, 1)
                    if value == "+":
                        result = num1 + num2
                        stack.append(result)
                    if value == "-":
                        # print(str(num1) + " - " + str(num2))
                        result = num1 - num2
                        stack.append(result)
                    if value == "*":
                        result = num1 * num2
                        stack.append(result)
                    if value == "/":
                        # print(str(num1) + " / " + str(num2))
                        result = math.floor(num1 / num2)
                        stack.append(result)
                else:
                    stack.append(value)

            # print("scanned: " + str(value))
            # print("stack: " + str(stack))
        # print("done: " + str(stack))
        return stack[0]


    def traverse(self, targetValues, currentId):
        currentNode = self.parseTree[currentId]
        arrived = False
        while not arrived:
            if currentNode.parent == None:
                arrived = True
            else:
                parent = self.parseTree[currentNode.parent]
                if parent.value in targetValues:
                    arrived = True
                else:
                    currentNode = self.parseTree[parent.id]
                    if currentNode.value == None:
                        arrived = True
        return currentNode.id


    def roll(self, n, s):
        rolls = []
        for x in range(int(n)):
            rolls.append(random.randint(1, int(s)))
        return sum(rolls)
                
# ---------------------------------------------------------
class InvalidTokenError(Exception):
    pass


class ExtendedParser(DiceParser):

    def __init__(self):
        super().__init__()

    def populateVariables(self, tokens, variableDict):
        variables = []
        for x in range(len(tokens)):
            token = tokens[x]
            if not self.charIsNumeric(token) and not token in self.ops:
                if token in variableDict:
                    tokenExpression = self.tokenize(variableDict[token])
                    del tokens[x]
                    tokens = tokens[:x] + tokenExpression + tokens[x:]
                else:
                    raise InvalidTokenError(f"token \"{token}\" not recognized")
        return tokens


    def parse(self, diceString, variableDict):

        print(f"parsing '{diceString}'")

        # build tokens
        tokens = self.tokenize(diceString)
        tokens = self.populateVariables(tokens, variableDict)
        # print(tokens)

        # fix diceString
        stringList = []
        for token in tokens:
            stringList.append(str(token))
        self.diceString = "".join(stringList)

        # build and run
        self.buildParseTree(tokens)
        total = self.runParse()

        # format response
        resultString = self.diceString + f" = {str(total)}"
        resultString = resultString.replace("+", " + ")
        resultString = resultString.replace("*", " * ")
        resultString = resultString.replace("/", " / ")

        return resultString


if __name__ == "__main__":
    parser = ExtendedParser()

    nameSpace = {
        "spd": "2d20",
        "prof": "3",
        "dex": "-4"
    }
    dice = "1d20 + dex"
    print(parser.parse(dice, nameSpace))

    