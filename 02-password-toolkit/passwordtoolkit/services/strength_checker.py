import math
import re
import string

from passwordtoolkit.data.common_passwords import COMMON_PASSWORDS
from passwordtoolkit.domain.models import StrengthLevel, StrengthReport

SYMBOLS = string.punctuation
SEQUENCES = (
    string.ascii_lowercase,
    string.digits,
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm",
)


class StrengthChecker:
    """Scores a password out of 100 using length, variety and common-pattern penalties."""

    def check(self, password: str) -> StrengthReport:
        if not password:
            raise ValueError("Password cannot be empty.")

        has_lower = any(c in string.ascii_lowercase for c in password)
        has_upper = any(c in string.ascii_uppercase for c in password)
        has_digit = any(c in string.digits for c in password)
        has_symbol = any(c in SYMBOLS for c in password)
        length = len(password)
        suggestions: list[str] = []

        # Length: up to 40 points. Variety: 10 per character type. Bonus: 10 at 12+, 10 at 16+.
        score = min(length, 16) / 16 * 40
        score += 10 * sum([has_lower, has_upper, has_digit, has_symbol])
        score += 10 if length >= 12 else 0
        score += 10 if length >= 16 else 0

        if length < 12:
            suggestions.append("Use at least 12 characters.")
        if not has_lower:
            suggestions.append("Add lowercase letters.")
        if not has_upper:
            suggestions.append("Add uppercase letters.")
        if not has_digit:
            suggestions.append("Add numbers.")
        if not has_symbol:
            suggestions.append("Add symbols such as ! or #.")

        if self._has_repeats(password):
            score -= 10
            suggestions.append(
                "Avoid repeating the same character 3 or more times in a row."
            )
        if self._has_sequence(password):
            score -= 10
            suggestions.append("Avoid sequences such as abc, 123 or qwerty.")
        if password.lower() in COMMON_PASSWORDS:
            score = min(score, 10)
            suggestions.insert(
                0, "This is a very common password that attackers try first."
            )

        final_score = int(max(0, min(100, round(score))))
        return StrengthReport(
            score=final_score,
            level=self._level(final_score),
            entropy_bits=self._entropy(
                password, has_lower, has_upper, has_digit, has_symbol
            ),
            suggestions=suggestions,
        )

    @staticmethod
    def _has_repeats(password: str) -> bool:
        return re.search(r"(.)\1\1", password) is not None

    @staticmethod
    def _has_sequence(password: str) -> bool:
        lowered = password.lower()
        for sequence in SEQUENCES:
            for i in range(len(sequence) - 2):
                chunk = sequence[i : i + 3]
                if chunk in lowered or chunk[::-1] in lowered:
                    return True
        return False

    @staticmethod
    def _entropy(
        password: str, lower: bool, upper: bool, digit: bool, symbol: bool
    ) -> float:
        pool = 0
        pool += 26 if lower else 0
        pool += 26 if upper else 0
        pool += 10 if digit else 0
        pool += len(SYMBOLS) if symbol else 0
        return len(password) * math.log2(pool) if pool else 0.0

    @staticmethod
    def _level(score: int) -> StrengthLevel:
        if score < 30:
            return StrengthLevel.VERY_WEAK
        if score < 50:
            return StrengthLevel.WEAK
        if score < 70:
            return StrengthLevel.FAIR
        if score < 85:
            return StrengthLevel.STRONG
        return StrengthLevel.VERY_STRONG
