# Password Toolkit

A password strength checker and secure password generator with **two interfaces**: a desktop GUI with a live strength meter, and a command-line tool. Built with clean architecture and a pytest suite.

## Screenshots

**Desktop GUI: live strength meter**

![GUI check](docs/gui-check.png)

**Desktop GUI: generator**

![GUI generate](docs/gui-generate.png)

**Command line (typer + rich)**

![CLI](docs/cli.png)

## Features

- Scores passwords from 0 to 100 and rates them Very weak to Very strong
- Live feedback in the GUI as you type
- Estimates entropy in bits
- Detects common passwords, repeated characters (`aaa`) and sequences (`abc`, `123`, `qwerty`)
- Gives specific suggestions for improvement
- Generates random passwords (8-128 characters) with selectable character types
- Guarantees every selected character type appears in a generated password

## Security design

- **Cryptographically secure randomness:** generation uses Python's `secrets` module, not `random`, which is predictable.
- **Nothing stored or logged:** passwords exist only in memory while checked.
- **Masked input:** the GUI hides what you type by default, and the CLI offers a hidden prompt so the password never lands in shell history.
- **Clipboard hygiene:** copied passwords are cleared from the clipboard after 30 seconds (only if still unchanged).
- **Common-password blocklist:** known weak passwords are capped at a very low score, in line with NIST guidance. The bundled list is a small sample; a production version would load a large breached-password list.

## How scoring works

| Component | Points |
|---|---|
| Length (up to 16 characters) | 0-40 |
| Character variety (lowercase, uppercase, digits, symbols) | 10 each |
| Length bonus (12+ and 16+ characters) | 10 each |
| Repeated characters / sequences | -10 each |
| Common password | capped at 10 |

## Tech stack

Python 3.10+, Tkinter, typer, rich, pytest, ruff

## Getting started

```powershell
git clone https://github.com/asingh29pd/python-portfolio.git
cd python-portfolio
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
cd 02-password-toolkit
```

### Desktop GUI

```powershell
python main_gui.py
```

### Command line

```powershell
python main.py check                 # hidden password prompt (recommended)
python main.py check "MyP@ssw0rd"    # direct argument
python main.py generate              # one 16-character password
python main.py generate -l 24 -n 5   # five 24-character passwords
python main.py generate --no-symbols
```

## Architecture

```
interfaces/ (GUI, CLI)  ->  services/ (StrengthChecker, PasswordGenerator)  ->  data/
                            domain/ (models) is shared by every layer
```

```
02-password-toolkit/
├── passwordtoolkit/
│   ├── domain/          # StrengthReport, StrengthLevel, GeneratorOptions
│   ├── services/        # Scoring rules and secure generation
│   ├── data/            # Common-password list
│   └── interfaces/      # Tkinter GUI and typer/rich CLI
├── tests/               # pytest suite
├── main.py              # CLI entry point
└── main_gui.py          # GUI entry point
```

### Design decisions

- **No business logic in the interfaces:** the GUI and CLI only collect input and display results.
- **Dependency injection:** the GUI receives its checker and generator in its constructor, so they are easy to replace or test.
- **Immutable models:** results and options are frozen dataclasses.
- **No unneeded layers:** this project has no database, so it has no repository layer.

## Testing

```powershell
python -m pytest -v
```

27 tests cover scoring boundaries, common-password detection, repeat and sequence detection, entropy, generator length limits, character-type guarantees, exclusions and input validation.

## Possible improvements

- Load a large breached-password list (for example, hashed lists)
- Passphrase generation from a word list
- Export a strength report

## Author

Kishan Singh