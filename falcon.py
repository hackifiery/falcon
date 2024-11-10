import os
import sys
from compile import run

def run_file(filename):
    if not os.path.exists(filename):
        print(f"Error: File {filename} does not exist.")
        return

    with open(filename, "r") as f:
        code = f.read()
        run(code)


if __name__ == "__main__":
    run_file("test.fa")
    """if len(sys.argv) != 2:
        print("Usage: snowsnake <filename>")
    else:
        filename = sys.argv[1]
        run_file(filename)"""
