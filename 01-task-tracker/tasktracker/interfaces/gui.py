import tkinter as tk
from datetime import date, datetime
from tkinter import messagebox, ttk

from tasktracker.bootstrap import build_service
from tasktracker.domain.task import Priority
from tasktracker.services.task_service import TaskNotFoundError, TaskService

BG = "#f4f6fb"
ACCENT = "#3b5bdb"
FONT = "Segoe UI"


class TaskApp(tk.Tk):
    def __init__(self, service: TaskService):
        super().__init__()
        self.service = service
        self.title("Task Tracker")
        self.geometry("860x540")
        self.minsize(720, 420)
        self.configure(bg=BG)

        self._build_styles()
        self._build_form()
        self._build_table()
        self._build_buttons()
        self.refresh()

    # ---------- layout ----------
    def _build_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, font=(FONT, 10))
        style.configure("Header.TLabel", font=(FONT, 20, "bold"), foreground=ACCENT)
        style.configure("TCheckbutton", background=BG, font=(FONT, 10))
        style.configure("TButton", font=(FONT, 10), padding=6)
        style.configure("Accent.TButton", background=ACCENT, foreground="white")
        style.map("Accent.TButton", background=[("active", "#2f4ac0")])
        style.configure("Treeview", rowheight=30, font=(FONT, 10))
        style.configure("Treeview.Heading", font=(FONT, 10, "bold"))

    def _build_form(self) -> None:
        ttk.Label(self, text="Task Tracker", style="Header.TLabel").pack(
            anchor="w", padx=20, pady=(16, 4)
        )

        form = ttk.Frame(self)
        form.pack(fill="x", padx=20, pady=8)
        form.columnconfigure(0, weight=1)

        ttk.Label(form, text="Title").grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="Priority").grid(row=0, column=1, sticky="w", padx=(12, 0))
        ttk.Label(form, text="Due (YYYY-MM-DD)").grid(
            row=0, column=2, sticky="w", padx=(12, 0)
        )

        self.title_var = tk.StringVar()
        self.priority_var = tk.StringVar(value=Priority.MEDIUM.value)
        self.due_var = tk.StringVar()

        title_entry = ttk.Entry(form, textvariable=self.title_var)
        title_entry.grid(row=1, column=0, sticky="ew")
        title_entry.bind("<Return>", lambda event: self.add_task())
        title_entry.focus()

        ttk.Combobox(
            form,
            textvariable=self.priority_var,
            values=[p.value for p in Priority],
            state="readonly",
            width=10,
        ).grid(row=1, column=1, padx=(12, 0))

        ttk.Entry(form, textvariable=self.due_var, width=16).grid(
            row=1, column=2, padx=(12, 0)
        )

        ttk.Button(
            form, text="Add Task", style="Accent.TButton", command=self.add_task
        ).grid(row=1, column=3, padx=(12, 0))

    def _build_table(self) -> None:
        self.show_done = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            self,
            text="Show completed tasks",
            variable=self.show_done,
            command=self.refresh,
        ).pack(anchor="w", padx=20)

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=20, pady=8)

        columns = {
            "id": ("ID", 50),
            "title": ("Title", 340),
            "priority": ("Priority", 90),
            "due": ("Due", 150),
            "status": ("Status", 100),
        }
        self.tree = ttk.Treeview(
            container, columns=list(columns), show="headings", selectmode="browse"
        )
        for key, (label, width) in columns.items():
            self.tree.heading(key, text=label)
            self.tree.column(key, width=width, anchor="w")
        self.tree.column("title", stretch=True)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.tag_configure("high", foreground="#e03131")
        self.tree.tag_configure("medium", foreground="#e8890c")
        self.tree.tag_configure("low", foreground="#2f9e44")
        self.tree.tag_configure("overdue", foreground="#c92a2a")
        self.tree.tag_configure("done", foreground="#868e96")

    def _build_buttons(self) -> None:
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=20, pady=(0, 14))

        ttk.Button(bar, text="✓ Mark Done", command=self.complete_task).pack(
            side="left"
        )
        ttk.Button(bar, text="Delete", command=self.delete_task).pack(
            side="left", padx=8
        )

        self.status_var = tk.StringVar()
        ttk.Label(bar, textvariable=self.status_var).pack(side="right")

    # ---------- actions ----------
    def refresh(self) -> None:
        self.tree.delete(*self.tree.get_children())
        tasks = self.service.list_tasks(include_done=self.show_done.get())

        for task in tasks:
            overdue = bool(
                task.due_date and task.due_date < date.today() and not task.done
            )
            if task.done:
                tag = "done"
            elif overdue:
                tag = "overdue"
            else:
                tag = task.priority.value

            due_text = task.due_date.isoformat() if task.due_date else "-"
            if overdue:
                due_text += " (overdue)"
            status = "✓ Done" if task.done else "○ Pending"

            self.tree.insert(
                "",
                "end",
                iid=str(task.id),
                values=(
                    task.id,
                    task.title,
                    task.priority.value.title(),
                    due_text,
                    status,
                ),
                tags=(tag,),
            )

        pending = sum(1 for task in tasks if not task.done)
        self.status_var.set(f"{len(tasks)} shown  •  {pending} pending")

    def _selected_id(self) -> int | None:
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo(
                "No task selected", "Please click a task in the list first."
            )
            return None
        return int(selection[0])

    def add_task(self) -> None:
        due_text = self.due_var.get().strip()
        due = None
        if due_text:
            try:
                due = datetime.strptime(due_text, "%Y-%m-%d").date()
            except ValueError:
                messagebox.showerror(
                    "Invalid date", "Use the format YYYY-MM-DD, e.g. 2026-11-30."
                )
                return

        try:
            self.service.add_task(
                self.title_var.get(), Priority(self.priority_var.get()), due
            )
        except ValueError as error:
            messagebox.showerror("Cannot add task", str(error))
            return

        self.title_var.set("")
        self.due_var.set("")
        self.refresh()

    def complete_task(self) -> None:
        task_id = self._selected_id()
        if task_id is None:
            return
        try:
            self.service.complete_task(task_id)
        except TaskNotFoundError as error:
            messagebox.showerror("Error", str(error))
        self.refresh()

    def delete_task(self) -> None:
        task_id = self._selected_id()
        if task_id is None:
            return
        if not messagebox.askyesno("Delete task", f"Delete task #{task_id}?"):
            return
        try:
            self.service.delete_task(task_id)
        except TaskNotFoundError as error:
            messagebox.showerror("Error", str(error))
        self.refresh()


def run() -> None:
    try:  # sharper text on Windows high-DPI screens
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    TaskApp(build_service()).mainloop()
