import pytest

from passwordtoolkit.domain.models import StrengthLevel
from passwordtoolkit.services.strength_checker import StrengthChecker


@pytest.fixture
def checker():
    return StrengthChecker()


def test_empty_password_raises(checker):
    with pytest.raises(ValueError, match="empty"):
        checker.check("")


def test_common_password_is_very_weak(checker):
    report = checker.check("password")

    assert report.level == StrengthLevel.VERY_WEAK
    assert report.score <= 10
    assert "common" in report.suggestions[0].lower()


def test_common_password_check_ignores_case(checker):
    report = checker.check("Password1")

    assert report.level == StrengthLevel.VERY_WEAK


def test_short_password_is_very_weak(checker):
    assert checker.check("abc").level == StrengthLevel.VERY_WEAK


def test_long_mixed_password_is_very_strong(checker):
    report = checker.check("Tr0ub4dor&3xK9!vQ")

    assert report.level == StrengthLevel.VERY_STRONG
    assert report.score == 100
    assert report.suggestions == []


def test_repeated_characters_are_flagged(checker):
    report = checker.check("Aaaa1111!zz")

    assert any("repeating" in tip.lower() for tip in report.suggestions)


def test_sequences_are_flagged(checker):
    report = checker.check("Xabc!7Kp2m9Q")

    assert any("sequence" in tip.lower() for tip in report.suggestions)


def test_missing_character_types_give_suggestions(checker):
    report = checker.check("alllowercaseletters")

    tips = " ".join(report.suggestions).lower()
    assert "uppercase" in tips
    assert "numbers" in tips
    assert "symbols" in tips


def test_longer_password_has_more_entropy(checker):
    short = checker.check("aB3$aB3$")
    long = checker.check("aB3$aB3$aB3$")

    assert long.entropy_bits > short.entropy_bits


@pytest.mark.parametrize(
    "password", ["a", "password", "Tr0ub4dor&3xK9!vQ", "x" * 200, "!!!!!!!!!!!!"]
)
def test_score_always_between_0_and_100(checker, password):
    assert 0 <= checker.check(password).score <= 100
