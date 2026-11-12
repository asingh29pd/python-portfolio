import secrets
import string

from passwordtoolkit.domain.models import GeneratorOptions

MIN_LENGTH = 8
MAX_LENGTH = 128


class PasswordGenerator:
    """Generates passwords with `secrets`, Python's cryptographically secure random source."""

    def generate(self, options: GeneratorOptions) -> str:
        if not MIN_LENGTH <= options.length <= MAX_LENGTH:
            raise ValueError(f"Length must be between {MIN_LENGTH} and {MAX_LENGTH}.")

        pools = self._selected_pools(options)
        if not pools:
            raise ValueError("Select at least one character type.")

        # Guarantee one character from every selected type, fill the rest randomly, then shuffle.
        all_characters = "".join(pools)
        characters = [secrets.choice(pool) for pool in pools]
        characters += [
            secrets.choice(all_characters)
            for _ in range(options.length - len(characters))
        ]
        secrets.SystemRandom().shuffle(characters)
        return "".join(characters)

    @staticmethod
    def _selected_pools(options: GeneratorOptions) -> list[str]:
        pools = []
        if options.use_lowercase:
            pools.append(string.ascii_lowercase)
        if options.use_uppercase:
            pools.append(string.ascii_uppercase)
        if options.use_digits:
            pools.append(string.digits)
        if options.use_symbols:
            pools.append(string.punctuation)
        return pools
