import pytest
from src.task2 import identify_data_type

@pytest.mark.parametrize("test_input, expected_output", [
    (42, "integer"),
    (3.14159, "float"),
    ("DevEdu Container", "string"),
    (True, "boolean"), 
    (False, "boolean")
])

def test_identify_data_type(test_input, expected_output):
    assert identify_data_type(test_input) == expected_output