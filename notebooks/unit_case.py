from pydantic import BaseModel

def add_two_numbers(a: int, b: int) -> int:
    return a + b


def test_add():
    assert add_two_numbers(2, 3) == 6