def get_favorite_books():
    return [
        "Dune by Frank Herbert",
        "House of Leaves by Mark Z. Danielewski",
        "Fahrenheit 451 by Ray Bradbury",
        "S. by J.J. Abrams",
        "Lord of the Flies by William Golding"
    ]

def print_first_three_books(books):
    first_three = books[:3]
    for book in first_three:
        print(book)
    return first_three

def get_student_database():
    return {
        "Alice Smith": 1001,
        "Bob Jones": 1002,
        "Charlie Brown": 1003
    }