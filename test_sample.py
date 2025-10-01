from falcon import run_file
import pytest
import sys
from io import StringIO

def test_answer():
    with pytest.raises(SystemExit):
        stdin_bak = sys.stdin
        sys.stdin = StringIO("3")
        run_file("test.fa")
        sys.stdin = stdin_bak