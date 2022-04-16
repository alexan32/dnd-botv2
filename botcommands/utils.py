import asyncio
from pprint import pprint

async def deleteAfter(ctx, seconds):
    await asyncio.sleep(seconds)
    await ctx.message.delete()


def navigateDict(dictionary:dict, cwd:str, relative_path:str, delimeter="/"):
    tree = dictionary.copy()
    queue = relative_path.split(delimeter)
    stack = cwd.split(delimeter) if cwd != "" else []
    
    # build path
    if relative_path == "root":
        stack = []
        cwd = ""
    else:
        if relative_path == "." or relative_path == "":
            queue = []
        for segment in queue:
            if segment == "..":
                stack.pop()
            elif segment == ".":
                return cwd, dictionary, "\"./\" is unsupported."
            else:
                stack.append(segment)
   
    # process path
    testPath = delimeter.join(stack)
    try:
        for key in stack:
            tree = tree[key]
    except Exception as e:
        return cwd, dictionary, f"path \"{testPath}\" is invalid. {e} does not exist."

    return testPath, tree, "ok"


if __name__ == "__main__":

    directory = {
        "player": {
            "rolls": {
                "dex": "3"
            },
            "bonus": {
                "stuff": {
                    "prof": "2"
                }
            }
        }
    }

    def get(relPath, default="0", delimeter="/"):
        cwd, value, message = navigateDict(directory, "", relPath, delimeter=delimeter)
        print(message)
        if type(value) is dict:
            return default
        return value

    print(navigateDict(directory, "", ""))

    # print('get("player/rolls/dex")')
    # print(get("player/rolls/dex"))

    # print('\nget("player/rolls/str")')
    # print(get("player/rolls/str"))

    # print('\nget("player/rolls/str", "7")')
    # print(get("player/rolls/str", "7"))

    # print('\nget("player/rolls/str", "7")')
    # print(get("player/rolls/str", "7"))