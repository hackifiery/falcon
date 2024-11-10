import operator as op
import pathlib
import ast
import os
import glob
import importlib

libs = {}
# Clear the console and vars files
open("console", "w").close()
open("vars", "w").close()

tmpcount = 0

# Operators mapping
operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.BitXor: op.xor,
    ast.USub: op.neg
}
class CommandNotFoundError(ValueError): pass

def eval_expr(expr):
    return eval_(ast.parse(expr, mode='eval').body)

def clearfile(file:str):
    open(file[1:], "w").close()

def eval_(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return node.value
    elif isinstance(node, ast.BinOp):
        return operators[type(node.op)](eval_(node.left), eval_(node.right))
    elif isinstance(node, ast.UnaryOp):
        return operators[type(node.op)](eval_(node.operand))
    else:
        raise TypeError(f"Unsupported operation: {ast.dump(node)}")

def loadvar(var: str):
    with open("vars", "r") as v:
        for line in v:
            if line.split()[0] == var:
                return ' '.join(line.split()[1:])
    return ""

def do_op(operation: str):
    if operation.startswith("!") and operation.endswith("!"):
        return eval_expr(operation[1:-1])
    else:
        raise ValueError(f"Invalid operation format: {operation}")

def include(file: str):
    lib = file.split(".")[0]
    mod = file.split(".")[1]
    try:
        # Import the module dynamically
        module = importlib.import_module(f"library.{lib}.{mod}")
        libs[mod] = module  # Store by module name for easy access
    except ModuleNotFoundError:
        print(f"Error: library '{file}' not found.")
def read(file):
    if file.startswith("@"):
        filename = file[1:]
        try:
            with open(filename, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return f"Error: {filename} not found."
    else:
        return f"Error: File name must start with '@'."

def mktmp():
    global tmpcount
    tmp_filename = "tmp" + (str(tmpcount) if tmpcount > 0 else "")
    with open(tmp_filename, "w") as tmp:
        tmp.write("")
        tmpcount += 1

def clear_tmp_files():
    global tmpcount
    for tmp_file in glob.glob("tmp*"):
        os.remove(tmp_file)
    tmpcount = 0

def string(text: str):
    converted = ""
    i = 0
    while i < len(text):
        if text[i-1] == "\\":
            converted += text[i]
            i += 1
            continue
        if text[i] == "\\":
            i+=1
            continue
        if text[i] == "$":
            j = i + 1
            while j < len(text) and text[j] != " ":
                j += 1
            converted += loadvar(text[i + 1:j])
            i = j
        elif text[i] == "!":
            j = i + 1
            while j < len(text) and text[j] != "!":
                j += 1
            converted += str(do_op(text[i:j + 1]))
            i = j + 1
        elif text[i] == ";":
            j = i + 1
            while j < len(text) and text[j] != ";":
                j += 1
            if text[i+1:j] == "endl":
                converted+="\n"
            elif text[i+1:j] == "ws":
                converted+=" "
            else:
                snippet_result = run_snippet(text[i + 1:j])
                converted += snippet_result
            i = j + 1
        else:
            converted += text[i]
            i += 1
    return converted

def run_snippet(snippet: str):
    """
    Run a single-line snippet command and return its output if available.
    """
    parts = snippet.split()
    output = None
    try:
        output = run_line(parts)
    except CommandNotFoundError as e:
        output = f"Error: {e}"
    return output if output is not None else ".voidobj"

def run_line(parts):
    """
    Execute a single line of code and handle included libraries.
    """
    com = parts[0]
    args = parts[1:]
    
    if com == "write" and args[0].startswith("@"):
        writetarget = args[0][1:]
        writetext = string(' '.join(args[1:]))
        with open(writetarget, "a") as f:
            f.write(writetext)
    elif com == "read" and args[0].startswith("@"):
        return read(args[0])
    elif com == "include":
        include(args[0])
    elif com == "mktmp":
        mktmp()
    elif com == "clrtmp":
        clear_tmp_files()
    elif com == "clrfile" and args[0].startswith("@"):
        clearfile(args[0])
    else:
        # Try to run the command as a function from an included library
        for mod_name, mod in libs.items():
            if hasattr(mod, com):
                func = getattr(mod, com)
                try:
                    result = func(*args)
                    return str(result) if result is not None else ".voidobj"
                except TypeError as e:
                    return f"Error calling {com}: {e}"
        raise CommandNotFoundError(f"Command not found: '{com}'")

def run(code):
    """
    Executes a full block of code line-by-line, managing temporary files and library functions.
    """
    clear_tmp_files()
    for line in code.splitlines():
        if not line or line.startswith("::"):
            continue
        try:
            run_line(line.split())
        except CommandNotFoundError as e:
            print(e)