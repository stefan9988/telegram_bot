import re
import pytest

from word_quiz import evaluate_answers, clean_words

def lines(out: str):
    return [ln.strip() for ln in out.strip().splitlines() if ln.strip()]

def test_all_correct_ignores_spaces_and_case():
    correct = [' alchemy', ' tenacity', ' vicissitude', 'insatiability']
    user    = ['Alchemy', 'tenacity', 'vicissitude', 'insatiability']

    out = evaluate_answers(correct, user)
    lns = lines(out)

    # 4 comparisons, no size-mismatch line
    assert len(lns) == 4
    assert all("✅ correct" in ln for ln in lns)
    # numbered 1..4
    assert lns[0].startswith("1.")
    assert lns[-1].startswith("4.")

def test_flags_incorrect_word_at_position():
    correct = ['alchemy', 'tenacity', 'vicissitude', 'insatiability']
    user    = ['alchemy', 'tenacity', 'vicious', 'insatiability']

    out = evaluate_answers(correct, user)
    lns = lines(out)

    assert "✅ correct" in lns[0]
    assert "✅ correct" in lns[1]
    assert "❌ incorrect" in lns[2]   # only the 3rd differs
    assert "✅ correct" in lns[3]

def test_list_size_mismatch_when_user_has_fewer():
    correct = ['alchemy', 'tenacity', 'vicissitude', 'insatiability']
    user    = ['alchemy', 'tenacity']

    out = evaluate_answers(correct, user)
    lns = lines(out)

    # min_len comparisons + 1 mismatch line
    assert len(lns) == 3
    assert "✅ correct" in lns[0] and "✅ correct" in lns[1]
    assert "List size mismatch:" in lns[2]
    # counts in the message are correct
    assert re.search(r"4 .* vs 2 .*", lns[2])

def test_list_size_mismatch_when_user_has_more():
    correct = ['alchemy', 'tenacity']
    user    = ['alchemy', 'tenacity', 'vicissitude']

    out = evaluate_answers(correct, user)
    lns = lines(out)

    assert len(lns) == 3
    assert "✅ correct" in lns[0] and "✅ correct" in lns[1]
    assert "List size mismatch:" in lns[2]
    assert re.search(r"2 .* vs 3 .*", lns[2])

@pytest.mark.parametrize(
    "raw, expected",
    [
        (["  Alchemy  ", "  TENACITY"], ["alchemy", "tenacity"]),
        ([" vicissitude\t", "\nInsatiability  "], ["vicissitude", "insatiability"]),
        (["  mixed  Case  "], ["mixed  case"]),   # inner spaces are preserved by strip().lower()
    ],
)
def test_clean_words_strips_and_lowercases(raw, expected):
    assert clean_words(raw) == expected
