from src.task1 import print_hello

def test_print_hello(capsys):
    print_hello()
    captured = capsys.readouterr()
    assert captured.out == "Hello, World!\n"