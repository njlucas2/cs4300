from src.task5 import get_favorite_books, print_first_three_books, get_student_database

def test_favorite_books_list():
    books = get_favorite_books()
    # Verify it is a list and contains enough books to slice
    assert isinstance(books, list)
    assert len(books) >= 3

def test_print_first_three_books(capsys):
    books = get_favorite_books()
    first_three = print_first_three_books(books)
    
    # Verify the slice contains exactly the first three items
    assert len(first_three) == 3
    assert first_three == books[:3]
    
    # Verify the console output matches the sliced books
    captured = capsys.readouterr()
    for book in first_three:
        assert book in captured.out

def test_student_database():
    student_db = get_student_database()
    
    # Verify it is a dictionary
    assert isinstance(student_db, dict)
    
    # Verify the database contains expected sample data and correct types
    assert "Alice Smith" in student_db
    assert isinstance(student_db["Alice Smith"], int)
    assert student_db["Bob Jones"] == 1002