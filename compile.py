import operator as op
import ast
import importlib

libs = {}
vars = {}

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

class CommandNotFoundError(ValueError):
    pass


def string(text: str) -> str:
    """Process strings with $, !expr!, ;snippet; substitutions."""
    converted = ""
    i = 0
    while i < len(text):
        if i > 0 and text[i - 1] == "\\":
            converted += text[i]
            i += 1
            continue

        if text[i] == "\\":
            i += 1
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
            snippet = text[i + 1:j]
            if snippet == "endl":
                converted += "\n"
            elif snippet == "ws":
                converted += " "
            else:
                snippet_result = run_snippet(snippet)
                if snippet_result != ".voidobj":
                    converted += snippet_result
            i = j + 1

        else:
            converted += text[i]
            i += 1
    return converted


def eval_expr(expr: str):
    return eval_(ast.parse(string(expr), mode="eval").body)


def eval_(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    elif isinstance(node, ast.Name):  # handle variables
        if node.id.startswith("$"):
            val = loadvar(node.id[1:])
        else:
            raise Exception
        try:
            return float(val) if "." in val else int(val)
        except ValueError:
            raise TypeError(f"Variable '{node.id}' is not numeric: {val!r}")
    elif isinstance(node, ast.BinOp):
        return operators[type(node.op)](eval_(node.left), eval_(node.right))
    elif isinstance(node, ast.UnaryOp):
        return operators[type(node.op)](eval_(node.operand))
    else:
        raise TypeError(f"Unsupported operation: {ast.dump(node)}")


def loadvar(var: str) -> str:
    return vars.get(var, "")


def setvar(name: str, val: str):
    val = string(val)
    if val.startswith("!") and val.endswith("!"):  # evaluate expression
        val = str(do_op(val))
    vars[name] = val


def do_op(operation: str):
    if operation.startswith("!") and operation.endswith("!"):
        for var in vars:
            operation = operation.replace(f"!${var}!", str(vars[var]))
        return eval_expr(operation[1:-1])
    raise ValueError(f"Invalid operation format: {operation}")


def include(file: str):
    lib, mod = file.split(".")
    try:
        module = importlib.import_module(f"library.{lib}.{mod}")
        libs[mod] = module
    except ModuleNotFoundError:
        print(f"Error: library '{file}' not found.")


def run_snippet(snippet: str):
    """Run a single-line snippet and return its result."""
    parts = snippet.split()
    if not parts:
        return ".voidobj"
    try:
        return run_line(parts)
    except CommandNotFoundError as e:
        return f"Error: {e}"


def run_line(parts):
    """Execute a single line of code."""
    com, *args = parts

    if com == "include":
        include(args[0])
        return ".voidobj"

    if com == "let":
        if len(args) >= 1 and "=" in args[0]:
            # form: let x=5
            name, val = args[0].split("=", 1)
            setvar(name, val)
        elif len(args) >= 3 and args[1] == "=":
            # form: let x = 5 (with spaces)
            name = args[0]
            val = " ".join(args[2:])   # <--- fix here
            setvar(name, val)
        return ".voidobj"

    # fallback: look in libraries
    for mod in libs.values():
        if hasattr(mod, com):
            func = getattr(mod, com)
            result = func(*args)
            return str(result) if result is not None else ".voidobj"

    raise CommandNotFoundError(f"Command not found: '{com}'")


def run(code: str):
    """Execute multi-line code block."""
    for line in code.splitlines():
        if not line or line.startswith("::"):
            continue
        try:
            run_line(line.split())
        except CommandNotFoundError as e:
            print(e)
