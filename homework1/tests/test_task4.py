import pytest
from src.task4 import calculate_discount

@pytest.mark.parametrize("price, discount, expected", [
    (100, 20, 80.0),
    (50.50, 10.0, 45.45),
    (200, 15.5, 169.0),
    (89.99, 0, 89.99),
    ("100", "20", 80.0)
])

def test_calculate_discount_valid_types(price, discount, expected):
    assert calculate_discount(price, discount) == expected

def test_calculate_discount_input_validation():
    with pytest.raises(ValueError, match="Invalid input"):
        calculate_discount("apple", 20)
        
    with pytest.raises(ValueError, match="cannot be negative"):
        calculate_discount(-50, 10)