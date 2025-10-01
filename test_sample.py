from falcon import run_file
import pytest

def test_answer():
    with pytest.raises(SystemExit):
        run_file("test.fa")