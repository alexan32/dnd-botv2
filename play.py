import json

model = {
        "first": 'first',
        "last": 'last',
        "id": 0,
        "balance": 0,
        "rolls": {},                # contains dice rolls
        "inventory": {},            # contains simplified item data
        "counters": {},             # contains counters. min, max, current
        "misc": {}                  # free space for extensions
    }

stringModel = '{"first": "", "last": "", "id": 0, "balance": 0, "rolls": {}, "inventory": {}, "counters": {}, "misc": {}}'
print(stringModel)
print(json.loads(stringModel))