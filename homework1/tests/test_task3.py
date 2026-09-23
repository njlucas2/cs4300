import pytest
from src.task3 import check_sign, get_first_ten_primes, sum_to_one_hundred

@pytest.mark.parametrize("test_input, expected", [
    (5, "positive"),
    (0.001, "positive"),
    (-3, "negative"),
    (-99.9, "negative"),
    (0, "zero"),
    (0.0, "zero")  # Edge case: zero as a float
])

def test_check_sign(test_input, expected):
    assert check_sign(test_input) == expected

def test_get_first_ten_primes(capsys):
    expected_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    
    # Verify the function returns the correct list
    assert get_first_ten_primes() == expected_primes
    
    # Verify the printed output matches the requirements
    captured = capsys.readouterr()
    expected_output = "\n".join(map(str, expected_primes)) + "\n"
    assert captured.out == expected_output

def test_sum_to_one_hundred():
    # The sum of 1 to 100 is 5050
    assert sum_to_one_hundred() == 5050