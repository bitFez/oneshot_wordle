import random
import pytest

from .functions import get_random_clues
from .models import Word


def score_for_word(target: str, cand: str) -> int:
    target = target.lower()
    cand = cand.lower()
    bulls = sum(1 for i in range(min(len(cand), len(target))) if cand[i] == target[i])
    cows_set = set()
    for i, ch in enumerate(cand):
        if i < len(target) and ch == target[i]:
            continue
        if ch in target:
            cows_set.add(ch)
    cows = len(cows_set)
    return bulls * 3 + cows


@pytest.mark.django_db
def test_get_random_clues_returns_similar_words():
    # make deterministic
    random.seed(0)

    target = "cater"
    # create words in DB (including highly-related words)
    words = [
        "caper",
        "cater",
        "crate",
        "caret",
        "react",
        "trace",
        "dater",
        "later",
        "racer",
        "caste",
        "other",
        "zebra",
    ]
    for w in words:
        Word.objects.create(word=w)

    clues = get_random_clues(target, difficulty="regular")
    assert isinstance(clues, list)
    assert len(clues) == 5
    # none of the clues should be the target
    assert target not in clues

    # compute scores for all candidates
    candidate_words = [w for w in words if w != target]
    scored = sorted([(w, score_for_word(target, w)) for w in candidate_words], key=lambda x: x[1], reverse=True)

    # instead of requiring a specific top candidate (which bulls-cap may exclude),
    # assert that at least one returned clue is reasonably informative: its score
    # must be >= the median candidate score
    candidate_scores = [s for _, s in scored]
    median_score = sorted(candidate_scores)[len(candidate_scores) // 2]
    clue_scores = [score_for_word(target, c) for c in clues]
    assert max(clue_scores) >= median_score, f"Clues {clues} are not informative (max score {max(clue_scores)} < median {median_score})"


@pytest.mark.django_db
def test_get_random_clues_easy_vs_regular():
    random.seed(1)
    target = "angel"
    words = [
        "angle",
        "angel",
        "anger",
        "anglo",
        "baker",
        "range",
        "align",
        "mango",
        "angle",
    ]
    # create fresh words
    Word.objects.all().delete()
    for w in words:
        Word.objects.create(word=w)

    clues_easy = get_random_clues(target, difficulty="easy")
    clues_regular = get_random_clues(target, difficulty="regular")

    assert isinstance(clues_easy, list) and len(clues_easy) == 5
    assert isinstance(clues_regular, list) and len(clues_regular) == 5
    # both should avoid the exact target
    assert target not in clues_easy
    assert target not in clues_regular


@pytest.mark.django_db
def test_easy_and_regular_have_different_primary(monkeypatch):
    # deterministic DB setup
    random.seed(3)
    target = "cater"
    words = [
        "caper",
        "cater",
        "crate",
        "caret",
        "react",
        "trace",
        "dater",
        "later",
        "racer",
        "zebra",
    ]
    Word.objects.all().delete()
    for w in words:
        Word.objects.create(word=w)

    # easy picks best-scoring primary
    clues_easy = get_random_clues(target, difficulty="easy")
    assert isinstance(clues_easy, list) and len(clues_easy) == 5

    # force regular mode's random.choice to pick the last candidate (unlikely to be top-scoring)
    monkeypatch.setattr('oneshot_guessle.game.functions.random.choice', lambda seq: seq[-1])
    clues_regular = get_random_clues(target, difficulty="regular")
    assert isinstance(clues_regular, list) and len(clues_regular) == 5

    # primaries should differ
    assert clues_easy[0] != clues_regular[0], f"easy primary {clues_easy[0]} should differ from regular primary {clues_regular[0]}"


@pytest.mark.django_db
def test_clues_do_not_reveal_all_positions():
    # deterministic DB setup where some candidates could reveal all positions
    target = "spare"
    words = [
        "spare",  # target
        "spear",  # many bulls in different positions
        "spark",
        "shape",
        "share",
        "stare",
        "shale",
        "smear",
        "scale",
    ]
    Word.objects.all().delete()
    for w in words:
        Word.objects.create(word=w)

    clues_reg = get_random_clues(target, difficulty="regular")
    clues_easy = get_random_clues(target, difficulty="easy")

    def revealed_positions(clues):
        pos = set()
        for c in clues:
            for i, ch in enumerate(c):
                if i < len(target) and ch == target[i]:
                    pos.add(i)
        return pos

    assert len(revealed_positions(clues_reg)) < len(target), f"regular revealed all positions: {clues_reg}"
    assert len(revealed_positions(clues_easy)) < len(target), f"easy revealed all positions: {clues_easy}"
