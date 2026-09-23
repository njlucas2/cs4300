import pytest
from src.task6 import count_words_in_file

@pytest.mark.parametrize("filepath, expected_count", [
    ("task6_read_me.txt", 104)
])
def test_count_words_in_file(filepath, expected_count):
    # This assumes pytest is run from the homework1 directory, 
    # where task6_read_me.txt is located.
    assert count_words_in_file(filepath) == expected_count

def test_count_words_file_not_found():
    # Verify the function handles missing files properly
    with pytest.raises(FileNotFoundError, match="Could not find the file"):
        count_words_in_file("does_not_exist.txt")