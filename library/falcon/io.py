from compile import string

def writeln(*args):
    """Print with expansion."""
    writetext = string(" ".join(args))
    print(writetext)
    return ".voidobj"

def readln():
    """Read input from user."""
    return input()