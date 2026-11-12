from typing import Optional

import typer
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel

from passwordtoolkit.domain.models import GeneratorOptions, StrengthLevel
from passwordtoolkit.services.password_generator import PasswordGenerator
from passwordtoolkit.services.strength_checker import StrengthChecker

app = typer.Typer(
    help="Password Toolkit: check password strength and generate secure passwords.",
    add_completion=False,
)
console = Console()
checker = StrengthChecker()
generator = PasswordGenerator()

LEVEL_STYLE = {
    StrengthLevel.VERY_WEAK: "bold red",
    StrengthLevel.WEAK: "red",
    StrengthLevel.FAIR: "yellow",
    StrengthLevel.STRONG: "green",
    StrengthLevel.VERY_STRONG: "bold green",
}


def fail(message: str) -> None:
    console.print(f"[bold red]✗[/bold red] {message}")
    raise typer.Exit(code=1)


@app.command()
def check(
    password: Optional[str] = typer.Argument(
        None, help="Password to check. Leave empty to type it hidden (safer)."
    ),
):
    """Check how strong a password is."""
    if password is None:
        password = typer.prompt("Enter password", hide_input=True)

    try:
        report = checker.check(password)
    except ValueError as error:
        fail(str(error))

    style = LEVEL_STYLE[report.level]
    filled = report.score // 5
    bar = "█" * filled + "░" * (20 - filled)
    body = (
        f"[{style}]{report.level.value}[/]  {report.score}/100\n"
        f"[{style}]{bar}[/]\n"
        f"Estimated entropy: {report.entropy_bits:.0f} bits"
    )
    if report.suggestions:
        body += "\n\n[bold]Suggestions[/bold]\n" + "\n".join(
            f"• {tip}" for tip in report.suggestions
        )

    console.print(
        Panel(body, title="Password Strength", border_style=style, expand=False)
    )


@app.command()
def generate(
    length: int = typer.Option(16, "--length", "-l", help="Password length (8-128)"),
    count: int = typer.Option(
        1, "--count", "-n", min=1, max=20, help="How many passwords to generate"
    ),
    no_uppercase: bool = typer.Option(
        False, "--no-uppercase", help="Leave out uppercase letters"
    ),
    no_digits: bool = typer.Option(False, "--no-digits", help="Leave out numbers"),
    no_symbols: bool = typer.Option(False, "--no-symbols", help="Leave out symbols"),
):
    """Generate secure random passwords."""
    options = GeneratorOptions(
        length=length,
        use_uppercase=not no_uppercase,
        use_digits=not no_digits,
        use_symbols=not no_symbols,
    )
    try:
        for _ in range(count):
            password = generator.generate(options)
            level = checker.check(password).level
            console.print(
                f"[bold]{escape(password)}[/bold]  [{LEVEL_STYLE[level]}]{level.value}[/]",
                highlight=False,
            )
    except ValueError as error:
        fail(str(error))
