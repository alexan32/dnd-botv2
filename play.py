

tokens = ['d', '6', '+', 'd', '20']

def find(list, token):
    indices = []
    for x in range(len(list)):
        if list[x] == token:
            indices.append(x)
    return indices

print(find(tokens, 'd'))