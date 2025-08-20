import os

from quote_of_the_day import extract_word_from_message, save_word_to_file, get_learned_words


def test_extract_word_from_message():
    msg = "C-Level Word: *Synergy*\nDefinition: working together"
    assert extract_word_from_message(msg) == "Synergy"


def test_save_and_get_learned_words(tmp_path):
    file_path = tmp_path / "words.txt"
    save_word_to_file("Alpha", str(file_path))
    save_word_to_file("Beta", str(file_path))
    assert os.path.exists(file_path)
    assert get_learned_words(str(file_path)) == "Alpha, Beta, "
