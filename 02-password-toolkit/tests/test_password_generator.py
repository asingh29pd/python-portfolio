import string

import pytest

from passwordtoolkit.domain.models import GeneratorOptions
from passwordtoolkit.services.password_generator import PasswordGenerator
from passwordtoolkit.services.strength_checker import StrengthChecker


@pytest.fixture
def generator():
    return PasswordGenerator()


@pytest.mark.parametrize("length", [8, 16, 64, 128])
def test_generated_password_has_requested_length(generator, length):
    assert len(generator.generate(GeneratorOptions(length=length))) == length


def test_every_selected_type_is_present(generator):
    for _ in range(50):
        password = generator.generate(GeneratorOptions(length=8))

        assert any(c in string.ascii_lowercase for c in password)
        assert any(c in string.ascii_uppercase for c in password)
        assert any(c in string.digits for c in password)
        assert any(c in string.punctuation for c in password)


def test_disabled_types_are_excluded(generator):
    options = GeneratorOptions(length=64, use_symbols=False, use_digits=False)

    password = generator.generate(options)

    assert all(c in string.ascii_letters for c in password)


def test_no_character_types_raises(generator):
    options = GeneratorOptions(
        use_lowercase=False, use_uppercase=False, use_digits=False, use_symbols=False
    )

    with pytest.raises(ValueError, match="at least one"):
        generator.generate(options)


@pytest.mark.parametrize("bad_length", [7, 129, 0, -5])
def test_invalid_length_raises(generator, bad_length):
    with pytest.raises(ValueError, match="between"):
        generator.generate(GeneratorOptions(length=bad_length))


def test_two_generated_passwords_differ(generator):
    options = GeneratorOptions(length=16)

    assert generator.generate(options) != generator.generate(options)


def test_default_generated_passwords_rate_strong_or_better(generator):
    checker = StrengthChecker()

    for _ in range(50):
        assert checker.check(generator.generate(GeneratorOptions())).score >= 70
