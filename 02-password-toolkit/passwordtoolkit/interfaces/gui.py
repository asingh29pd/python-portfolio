import tkinter as tk
from tkinter import messagebox, ttk

from passwordtoolkit.domain.models import GeneratorOptions, StrengthLevel
from passwordtoolkit.services.password_generator import PasswordGenerator
from passwordtoolkit.services.strength_checker import StrengthChecker

BG = "#f4f6fb"
ACCENT = "#3b5bdb"
FONT = "Segoe UI"
CLIPBOARD_CLEAR_MS = 30_000

LEVEL_COLOR = {
    StrengthLevel.VERY_WEAK: "#e03131",
    StrengthLevel.WEAK: "#f76707",
    StrengthLevel.FAIR: "#f59f00",
    StrengthLevel.STRONG: "#2f9e44",
    StrengthLevel.VERY_STRONG: "#087f5b",
}


class PasswordApp(tk.Tk):
    def __init__(self, checker: StrengthChecker, generator: PasswordGenerator):
        super().__init__()
        self.checker = checker
        self.generator = generator
        self._copied_password = ""

        self.title("Password Toolkit")
        self.geometry("620x520")
        self.minsize(560, 480)
        self.configure(bg=BG)

        self._build_styles()
        ttk.Label(self, text="Password Toolkit", style="Header.TLabel").pack(
            anchor="w", padx=20, pady=(16, 0)
        )

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=12, pady=12)
        notebook.add(self._build_check_tab(notebook), text="  Check strength  ")
        notebook.add(self._build_generate_tab(notebook), text="  Generate  ")

    # ---------- styles ----------
    def _build_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, font=(FONT, 10))
        style.configure("TCheckbutton", background=BG, font=(FONT, 10))
        style.configure("Header.TLabel", font=(FONT, 20, "bold"), foreground=ACCENT)
        style.configure("Level.TLabel", font=(FONT, 14, "bold"))
        style.configure("Sub.TLabel", font=(FONT, 10, "bold"))
        style.configure("TButton", font=(FONT, 10), padding=6)
        style.configure("Accent.TButton", background=ACCENT, foreground="white")
        style.map("Accent.TButton", background=[("active", "#2f4ac0")])
        style.configure("TNotebook", background=BG)
        style.configure("TNotebook.Tab", font=(FONT, 10), padding=(14, 8))

        style.configure("Horizontal.TProgressbar", troughcolor="#dee2e6", background="#adb5bd", thickness=16)
        for level, color in LEVEL_COLOR.items():
            style.configure(
                f"{level.name}.Horizontal.TProgressbar",
                troughcolor="#dee2e6",
                background=color,
                thickness=16,
            )

    # ---------- check tab ----------
    def _build_check_tab(self, parent: ttk.Notebook) -> ttk.Frame:
        frame = ttk.Frame(parent, padding=20)

        ttk.Label(frame, text="Enter a password").pack(anchor="w")
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(
            frame, textvariable=self.password_var, show="•", font=(FONT, 12)
        )
        self.password_entry.pack(fill="x", pady=(4, 6))
        self.password_entry.focus()

        self.show_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            frame, text="Show password", variable=self.show_var, command=self._toggle_show
        ).pack(anchor="w")

        self.meter = ttk.Progressbar(frame, maximum=100, length=300)
        self.meter.pack(fill="x", pady=(18, 8))

        self.level_var = tk.StringVar(value="Start typing to see the strength")
        self.level_label = ttk.Label(frame, textvariable=self.level_var, style="Level.TLabel")
        self.level_label.pack(anchor="w")

        self.entropy_var = tk.StringVar()
        ttk.Label(frame, textvariable=self.entropy_var).pack(anchor="w", pady=(2, 0))

        ttk.Label(frame, text="Suggestions", style="Sub.TLabel").pack(anchor="w", pady=(16, 2))
        self.tips_var = tk.StringVar()
        ttk.Label(frame, textvariable=self.tips_var, justify="left", wraplength=540).pack(anchor="w")

        # Registered last, so every widget it updates already exists.
        self.password_var.trace_add("write", lambda *_: self._update_strength())
        return frame

    def _toggle_show(self) -> None:
        self.password_entry.configure(show="" if self.show_var.get() else "•")

    def _update_strength(self) -> None:
        password = self.password_var.get()
        if not password:
            self.meter.configure(value=0, style="Horizontal.TProgressbar")
            self.level_var.set("Start typing to see the strength")
            self.level_label.configure(foreground="#495057")
            self.entropy_var.set("")
            self.tips_var.set("")
            return

        report = self.checker.check(password)
        self.meter.configure(value=report.score, style=f"{report.level.name}.Horizontal.TProgressbar")
        self.level_var.set(f"{report.level.value}  ({report.score}/100)")
        self.level_label.configure(foreground=LEVEL_COLOR[report.level])
        self.entropy_var.set(f"Estimated entropy: {report.entropy_bits:.0f} bits")
        self.tips_var.set(
            "\n".join(f"•  {tip}" for tip in report.suggestions) or "Looks great. No suggestions."
        )

    # ---------- generate tab ----------
    def _build_generate_tab(self, parent: ttk.Notebook) -> ttk.Frame:
        frame = ttk.Frame(parent, padding=20)

        length_row = ttk.Frame(frame)
        length_row.pack(fill="x")
        ttk.Label(length_row, text="Length (8-128)").pack(side="left")
        self.length_var = tk.StringVar(value="16")
        ttk.Spinbox(length_row, from_=8, to=128, textvariable=self.length_var, width=6).pack(
            side="left", padx=10
        )

        self.lower_var = tk.BooleanVar(value=True)
        self.upper_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.symbols_var = tk.BooleanVar(value=True)
        options_frame = ttk.Frame(frame)
        options_frame.pack(fill="x", pady=(14, 6))
        for text, variable in (
            ("Lowercase (a-z)", self.lower_var),
            ("Uppercase (A-Z)", self.upper_var),
            ("Numbers (0-9)", self.digits_var),
            ("Symbols (!@#...)", self.symbols_var),
        ):
            ttk.Checkbutton(options_frame, text=text, variable=variable).pack(anchor="w", pady=1)

        ttk.Button(
            frame, text="Generate password", style="Accent.TButton", command=self._generate
        ).pack(anchor="w", pady=(10, 14))

        self.generated_var = tk.StringVar()
        ttk.Entry(
            frame, textvariable=self.generated_var, state="readonly", font=("Consolas", 12)
        ).pack(fill="x")

        self.generated_level_var = tk.StringVar()
        self.generated_level_label = ttk.Label(
            frame, textvariable=self.generated_level_var, style="Level.TLabel"
        )
        self.generated_level_label.pack(anchor="w", pady=(10, 4))

        copy_row = ttk.Frame(frame)
        copy_row.pack(fill="x", pady=(4, 0))
        ttk.Button(copy_row, text="Copy to clipboard", command=self._copy).pack(side="left")
        self.copy_status_var = tk.StringVar()
        ttk.Label(copy_row, textvariable=self.copy_status_var).pack(side="left", padx=12)
        return frame

    def _generate(self) -> None:
        try:
            length = int(self.length_var.get())
        except ValueError:
            messagebox.showerror("Invalid length", "Length must be a whole number between 8 and 128.")
            return

        options = GeneratorOptions(
            length=length,
            use_lowercase=self.lower_var.get(),
            use_uppercase=self.upper_var.get(),
            use_digits=self.digits_var.get(),
            use_symbols=self.symbols_var.get(),
        )
        try:
            password = self.generator.generate(options)
        except ValueError as error:
            messagebox.showerror("Cannot generate", str(error))
            return

        report = self.checker.check(password)
        self.generated_var.set(password)
        self.generated_level_var.set(f"{report.level.value}  ({report.score}/100)")
        self.generated_level_label.configure(foreground=LEVEL_COLOR[report.level])
        self.copy_status_var.set("")

    def _copy(self) -> None:
        password = self.generated_var.get()
        if not password:
            self.copy_status_var.set("Generate a password first.")
            return
        self.clipboard_clear()
        self.clipboard_append(password)
        self.update()  # helps the clipboard keep the text while the app stays open
        self._copied_password = password
        self.copy_status_var.set("Copied. Clipboard clears in 30 seconds.")
        self.after(CLIPBOARD_CLEAR_MS, self._clear_clipboard)

    def _clear_clipboard(self) -> None:
        try:
            if self.clipboard_get() == self._copied_password:
                self.clipboard_clear()
        except tk.TclError:
            pass  # clipboard was already empty or holds non-text data
        self.copy_status_var.set("")


def run() -> None:
    try:  # sharper text on Windows high-DPI screens
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    PasswordApp(StrengthChecker(), PasswordGenerator()).mainloop()