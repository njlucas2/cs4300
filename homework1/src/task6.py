def count_words_in_file(filepath):
    try:
        # 'with' ensures the file is safely closed after reading
        with open(filepath, 'r', encoding='utf-8') as file:
            contents = file.read()
            words = contents.split()
            return len(words)
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find the file: {filepath}")