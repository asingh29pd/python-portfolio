from dataclasses import dataclass, field
from enum import Enum


class StrengthLevel(str, Enum):
    VERY_WEAK = "Very weak"
    WEAK = "Weak"
    FAIR = "Fair"
    STRONG = "Strong"
    VERY_STRONG = "Very strong"


@dataclass(frozen=True)
class StrengthReport:
    score: int
    level: StrengthLevel
    entropy_bits: float
    suggestions: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class GeneratorOptions:
    length: int = 16
    use_lowercase: bool = True
    use_uppercase: bool = True
    use_digits: bool = True
    use_symbols: bool = True
