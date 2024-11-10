import pathlib
def consoleout():
    with open(str(pathlib.Path(__file__).parent.resolve())+"/../../console", "r") as console:
        print(console.read(), end="")
def consolein():
    return input()
#consoleout()