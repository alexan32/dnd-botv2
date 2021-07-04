import random


class Node:

    def __init__(self, id, token=None, parent=None, lc=None, rc=None):
        self.id = id
        self.parent = parent
        self.lc = lc
        self.rc = rc
        self.token = token
        self.data = None

    def setLc(self, node):
        self.lc = node.id
        node.parent = self.id
        return node

    def setRc(self, node):
        self.rc = node.id
        node.parent = self.id
        return node

    def toString(self):
        return f"{{id: {self.id}, token: {self.token}, parent: {self.parent}, lc: {self.lc}, rc: {self.rc}}}"


class Parser:

    operators = ['+', '-', '*', '/']
    functions = {
        'min': min,
        'max': max
    }
    counter = 0
    iterate = False


    def parse(self, diceString, nameSpace={}):
        tokens = self.tokenize(diceString, nameSpace)
        tokens = self.cleanTokens(tokens)
        tree = self.buildTree(tokens)
        if __name__ == '__main__':
            self.makeGraphViz(tree)
        total = self.computeTree(tree)
        diceString = self.buildString(tree, total)
        return total, diceString

    
    def tokenize(self, parseString, nameSpace={}):
        parseString = ''.join(parseString.split()).lower()
        tokens = []
        index = 0
        token = ''

        while True:
            current = parseString[index]
            _next = self.peek(parseString, index)
            token += current
            # print(f"index: {index} current: {current} next: {_next} token: {token}")

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

            elif current in self.operators or current in ['(', ',', ')']:
                tokens.append(token)
                token = ''

            index += 1
            if index == len(parseString):
                break
        
        # Perform replacements
        index = 0
        while index < len(tokens):
            token = tokens[index]
            if token in nameSpace.keys():
                newTokens = self.tokenize(nameSpace[token], nameSpace)
                tokens = tokens[:index] + newTokens + tokens[index+1:]
            index += 1
        return tokens

    
    def cleanTokens(self, tokens):
        index = 0
        while index < len(tokens) - 2:
            current = tokens[index]
            _next = tokens[index + 1] or None

            if current in self.operators and _next == '-':
                operand = tokens[index + 2] or None
                if operand.isnumeric():
                    num = int(operand)
                    num *= -1
                    tokens[index + 2] = str(num)
                    del tokens[index + 1]
            
            index += 1
        return tokens


    def buildTree(self, tokens):
        node = Node(self.getId())
        tree = {node.id : node}
        currentNodeId = node.id

        if len(tokens) == 1:
            node.token = tokens[0]
            return tree
        
        while True:
            currentToken = tokens.pop(0)
            currentNode = tree[currentNodeId]

            # NUMERIC: create child and populate with token
            if currentToken.isnumeric() or currentToken[1:].isnumeric():
                if currentNode.lc == None:
                    node = currentNode.setLc(Node(self.getId(), currentToken))
                else:
                    node = currentNode.setRc(Node(self.getId(), currentToken))
                tree[node.id] = node
                currentNodeId = node.id
                
            # D
            elif currentToken == 'd':
                child = tree[self.traverse(tree, currentNode.id, self.operators)]
                parent = tree[child.parent]
                # parent is root
                if parent.token == None:
                    parent.token = currentToken
                    currentNodeId = parent.id
                # perform swap
                else:
                    newNode = Node(self.getId(), token=currentToken)
                    tree[newNode.id] = newNode                          #   p        p
                    newNode.setLc(child)                                #    \        \
                    parent.setRc(newNode)                               #     c        n
                    currentNodeId = newNode.id                          #             /
                                                                        #            c
            # MULTIPLICATION
            elif currentToken in ['*', '/']:
                # go to first child of */
                child = tree[self.traverse(tree, currentNode.id, ['+', '-'])]
                parent = tree[child.parent]
                # populate empty root
                if parent.token == None:
                    parent.token = currentToken
                    currentNodeId = parent.id
                # insert node
                elif parent.token in ['+', '-'] or parent.parent != None:
                    newNode = Node(self.getId(), currentToken)
                    newNode.setLc(child)
                    parent.setRc(newNode)
                    tree[newNode.id] = newNode
                    currentNodeId = newNode.id
                # parent is root, create new root
                else:
                    newNode = Node(self.getId(), currentToken)
                    newNode.setLc(parent)
                    tree[newNode.id] = newNode
                    currentNodeId = newNode.id
                                        

            # ADDITION
            elif currentToken in ['+', '-']:
                # go to root
                child = tree[self.traverse(tree, currentNode.id)]
                root = tree[child.parent]
                # populate empty root
                if root.token == None:
                    root.token = currentToken
                    tree[root.id] = root
                    currentNodeId = root.id
                # make new root
                else:
                    newRoot = Node(self.getId(), currentToken)
                    newRoot.setLc(root)
                    tree[newRoot.id] = newRoot
                    currentNodeId = newRoot.id

            # FUNC
            elif currentToken in self.functions.keys():
                func = currentToken
                args = []
                arg = ''
                while True:
                    currentToken = tokens.pop(0)
                    if currentToken == '(':
                        pass
                    elif currentToken == ',':
                        args.append(arg)
                        arg = ''
                    elif currentToken == ')':
                        args.append(arg)
                        break
                    else:
                        arg += currentToken
                
                token = self.functions[func](args)
                tokens.insert(0, token)
                if __name__ == '__main__':
                    print(f"function: {func}, args: {args}")
                    print(f"result: {token}")
                
            else:
                raise Exception(f"Invalid token: '{currentToken}'")

            if len(tokens) == 0:
                break
            
            if __name__ == '__main__' and self.iterate:
                print("---------------------------------------------------------------------------------------")
                print(f"tokens: {tokens}")
                print(f"current Node: {currentNodeId}")
                self.printTree(tree)
                x = input()

        if __name__ == '__main__':
            self.printTree(tree)
        return tree
    

    def traverse(self, tree, currentId, targetValues=[]):
        currentNode = tree[currentId]
        count = 0

        while True:
            parent = tree[currentNode.parent]

            # parent is root
            if parent.parent == None:
                # print(f"traverse stopped at {currentNode.id}")
                return currentNode.id
            
            # parent has target value
            elif parent.token in targetValues:
                # print(f"traverse stopped at {currentNode.id}")
                return currentNode.id

            elif count > 100:
                print("parse tree is too large")
                raise Exception("traverse() function took to long. Parse tree is either too large or malformed.")

            else:
                count += 1
                currentNode = tree[parent.id]


    def computeTree(self, tree):
        computeStack = []
        visited = []
        currentNode = None
        for key in tree.keys():
            if tree[key].parent == None:
                currentNode = tree[key]        

        while True:
            
            if __name__ == '__main__' and self.iterate:
                print("--------------------------------------------")
                print(f"computeStack: {computeStack}\nvisited: {visited}\ncurrentNode: {currentNode.toString()}")
                x = input()

            # move to left child
            if currentNode.lc not in visited and currentNode.lc != None:
                currentNode = tree[currentNode.lc]

            # move to right child
            elif currentNode.rc not in visited and currentNode.rc != None:
                currentNode = tree[currentNode.rc]

            else:
                visited.append(currentNode.id)

                # perform compute
                if currentNode.token in ['+', '-', '*', '/', 'd']:
                    b = int(computeStack.pop())
                    a = int(computeStack.pop())
                    result = None

                    if currentNode.token == '+':
                        result = a + b
                    elif currentNode.token == '-':
                        result = a - b
                    elif currentNode.token == '*':
                        result = a * b
                    elif currentNode.token == '/':
                        result = int(a / b)
                    elif currentNode.token == 'd':
                        result = self.roll(a, b)
                        currentNode.data = result
                    computeStack.append(result)
                else:
                    computeStack.append(int(currentNode.token))

                # check for end or move to parent
                if currentNode.parent == None:
                    total = computeStack[0]
                    break
                else:
                    currentNode = tree[currentNode.parent]

        return total

    def buildString(self, tree, total):
        visited = []
        currentNode = None
        diceString = ''
        for key in tree.keys():
            if tree[key].parent == None:
                currentNode = tree[key] 

        while True:
            # move to left child
            if currentNode.lc not in visited and currentNode.lc != None:
                currentNode = tree[currentNode.lc]

            # process current node
            elif currentNode.id not in visited:
                diceString += f"{currentNode.token}"
                visited.append(currentNode.id)

            #  move to right child
            elif currentNode.rc not in visited and currentNode.rc != None:
                currentNode = tree[currentNode.rc]

            # current node already visited
            elif currentNode.id in visited:
                if currentNode.data != None:
                    diceString += f"({currentNode.data})"
                
                if currentNode.parent != None:
                    currentNode = tree[currentNode.parent]
                else:
                    break

        diceString += f" = {total}"
        for op in ['+', '-', '*', '/']:
            diceString = f' {op} '.join(diceString.split(op))

        return diceString


    def getId(self):
        self.counter += 1
        return str(self.counter)


    def makeGraphViz(self, tree):
        nodes = []
        paths = []
        for key in tree.keys():
            node = tree[key]
            nodes.append(f'\t{node.id} [label="{node.token}"]\n')
            if node.lc != None:
                paths.append(f'\t{node.id} -> {node.lc}\n')
            if node.rc != None:
                paths.append(f'\t{node.id} -> {node.rc}\n')

        nodeString = ""
        for node in nodes:
            nodeString += node 

        pathString = ""
        for path in paths:
            pathString += path

        diagram = f"digraph G {{\n{nodeString}\n{pathString}\n}}\nhttp://graphviz.it/#/"
        with open('parseTree.txt', 'w') as f:
            f.write(diagram)


    def printTree(self, tree):
        for key in tree.keys():
            print(tree[key].toString())


    def peek(self, parseString, index):
        try:
            return parseString[index + 1]
        except:
            return ''

    def roll(self, n, s):
        rolls = []
        for x in range(int(n)):
            rolls.append(random.randint(1, int(s)))
        return sum(rolls)


if __name__ == '__main__':
    parser = Parser()
    parser.iterate = True
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
    print(parser.parse("1d20 + prof + min(str, dex)", nameSpace)[1])
