"""
Batch-renames PDFs and sets their /Title (and /Author) metadata using pypdf.

The core logic (process_file, apply_pattern, read_existing_metadata) has no
GUI dependencies and can be imported and used headless. Run this file
directly to launch a tkinter GUI for building and running a batch.

Requires: pip install pypdf
"""

import os
import re
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, scrolledtext, ttk

from pypdf import PdfReader, PdfWriter

INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*]')


# ---------------------------------------------------------------------------
# Core logic (no GUI dependencies)
# ---------------------------------------------------------------------------

def extract_number(text):
    """Return the first run of digits found in `text` as an int, or None."""
    match = re.search(r"\d+", text)
    return int(match.group()) if match else None


def read_existing_metadata(file_path):
    """Return (title, author) from a PDF's existing metadata, defaulting to ''."""
    try:
        reader = PdfReader(str(file_path))
        meta = reader.metadata or {}
        return meta.get("/Title") or "", meta.get("/Author") or ""
    except Exception:
        return "", ""


def sanitize_filename(name):
    """Strip characters that aren't valid in Windows filenames."""
    return INVALID_FILENAME_CHARS.sub("", name).strip()


def apply_pattern(pattern, file_path, existing_title="", existing_author=""):
    """
    Substitute placeholders in `pattern`:
      {n}      - digits extracted from the file's original name
      {title}  - `existing_title` (typed manually or pulled from PDF metadata)
      {author} - `existing_author` (typed manually or pulled from PDF metadata)

    Returns the resulting string. Raises ValueError if the pattern is invalid
    (e.g. an unknown placeholder, or a format spec that doesn't fit the value).
    """
    number = extract_number(Path(file_path).stem)
    try:
        return pattern.format(n=number if number is not None else "",
                               title=existing_title, author=existing_author)
    except (KeyError, ValueError, IndexError) as e:
        raise ValueError(f"invalid pattern ({e})")


def process_file(file_path, title, author=None):
    """
    Rename `file_path` to "<title>.pdf" in the same folder and set the PDF's
    /Title (and /Author, if given) metadata.

    Does not raise on failure; every outcome (renamed/skipped/failed) is
    reported via the returned dict so a batch loop can continue past errors:
        {"status": "renamed" | "skipped" | "failed",
         "message": str, "old_path": Path, "new_path": Path or None}
    """
    old_path = Path(file_path)
    new_name = sanitize_filename(title or "")
    if not new_name:
        return {"status": "failed", "message": "empty/invalid title",
                "old_path": old_path, "new_path": None}

    new_path = old_path.with_name(f"{new_name}.pdf")

    if old_path == new_path:
        return {"status": "skipped", "message": "already named correctly",
                "old_path": old_path, "new_path": new_path}

    if new_path.exists():
        return {"status": "skipped", "message": f"target {new_path.name} already exists",
                "old_path": old_path, "new_path": new_path}

    try:
        reader = PdfReader(str(old_path))
        writer = PdfWriter()
        writer.append(reader)

        metadata = {"/Title": title}
        if author:
            metadata["/Author"] = author
        writer.add_metadata(metadata)

        with open(new_path, "wb") as f:
            writer.write(f)

        os.remove(old_path)
        return {"status": "renamed", "message": f"{old_path.name} -> {new_path.name}",
                "old_path": old_path, "new_path": new_path}

    except Exception as e:
        return {"status": "failed", "message": str(e), "old_path": old_path, "new_path": None}


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

EDITABLE_COLUMNS = ("title_pattern", "title", "author_pattern", "author")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF Renamer")
        self.geometry("900x600")

        self.rows = {}  # tree item id -> {"path": Path}
        self._added_paths = set()  # resolved path strings, to avoid duplicates

        self._build_widgets()

    def _build_widgets(self):
        title_row = ttk.Frame(self, padding=(8, 8, 8, 0))
        title_row.pack(fill="x")
        ttk.Label(title_row, text="Title pattern:", width=13).pack(side="left")
        self.title_pattern_var = tk.StringVar()
        self.title_pattern_entry = ttk.Entry(title_row, textvariable=self.title_pattern_var, width=40)
        self.title_pattern_entry.pack(side="left", padx=(4, 8), fill="x", expand=True)
        ttk.Button(title_row, text="Apply to All", command=self.apply_batch_title_pattern).pack(side="left")

        author_row = ttk.Frame(self, padding=(8, 4, 8, 0))
        author_row.pack(fill="x")
        ttk.Label(author_row, text="Author pattern:", width=13).pack(side="left")
        self.author_pattern_var = tk.StringVar()
        self.author_pattern_entry = ttk.Entry(author_row, textvariable=self.author_pattern_var, width=40)
        self.author_pattern_entry.pack(side="left", padx=(4, 8), fill="x", expand=True)
        ttk.Button(author_row, text="Apply to All", command=self.apply_batch_author_pattern).pack(side="left")

        self._active_pattern_entry = self.title_pattern_entry
        for entry in (self.title_pattern_entry, self.author_pattern_entry):
            entry.bind("<FocusIn>", lambda _e, w=entry: setattr(self, "_active_pattern_entry", w))

        builder = ttk.Frame(self, padding=(8, 4, 8, 0))
        builder.pack(fill="x")
        ttk.Label(builder, text="Insert into focused field:").pack(side="left")
        for label in ("{n}", "{n:03d}", "{title}", "{author}"):
            ttk.Button(builder, text=label, width=9,
                       command=lambda p=label: self._insert_placeholder(p)).pack(side="left", padx=2)

        sample = ttk.Frame(self, padding=(8, 4))
        sample.pack(fill="x")
        ttk.Label(sample, text="Sample title:").pack(side="left")
        self.title_sample_var = tk.StringVar()
        ttk.Label(sample, textvariable=self.title_sample_var, foreground="#555").pack(side="left", padx=(4, 16))
        ttk.Label(sample, text="Sample author:").pack(side="left")
        self.author_sample_var = tk.StringVar()
        ttk.Label(sample, textvariable=self.author_sample_var, foreground="#555").pack(side="left", padx=(4, 0))

        self.title_pattern_var.trace_add("write", lambda *_: self._update_sample())
        self.author_pattern_var.trace_add("write", lambda *_: self._update_sample())

        buttons = ttk.Frame(self, padding=(8, 4))
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Add Folder...", command=self.choose_folder).pack(side="left")
        ttk.Button(buttons, text="Add Files...", command=self.choose_files).pack(side="left", padx=(6, 0))
        ttk.Button(buttons, text="Move Up", command=self.move_row_up).pack(side="left", padx=(16, 0))
        ttk.Button(buttons, text="Move Down", command=self.move_row_down).pack(side="left", padx=(6, 0))
        self.run_button = ttk.Button(buttons, text="Run", command=self.run_batch)
        self.run_button.pack(side="right")

        progress_frame = ttk.Frame(self, padding=(8, 0))
        progress_frame.pack(fill="x")
        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate")
        self.progress_bar.pack(side="left", fill="x", expand=True)
        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(progress_frame, textvariable=self.progress_var).pack(side="left", padx=(8, 0))

        tree_frame = ttk.Frame(self, padding=(8, 4))
        tree_frame.pack(fill="both", expand=True)

        columns = ("file", "title_pattern", "title", "author_pattern", "author", "status")
        headings = ("File", "Title Pattern", "Title", "Author Pattern", "Author", "Status")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        for col, heading, width in zip(columns, headings, (160, 150, 170, 150, 120, 90)):
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, anchor="w")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="left", fill="y")

        self.tree.bind("<Double-1>", self._on_double_click)

        log_frame = ttk.Frame(self, padding=8)
        log_frame.pack(fill="both", expand=False)
        ttk.Label(log_frame, text="Log:").pack(anchor="w")
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, state="disabled")
        self.log_text.pack(fill="both", expand=True)

    def log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    # -- pattern builder / sample preview ------------------------------------

    def _insert_placeholder(self, placeholder):
        entry = self._active_pattern_entry
        entry.insert(tk.INSERT, placeholder)
        entry.focus()

    def _update_sample(self):
        children = self.tree.get_children()
        if children:
            row_id = children[0]
            path = self.rows[row_id]["path"]
            title = self.tree.set(row_id, "title")
            author = self.tree.set(row_id, "author")
        else:
            path, title, author = Path("example007.pdf"), "Sample Title", "Sample Author"

        def preview(pattern):
            if not pattern:
                return ""
            try:
                return apply_pattern(pattern, path, existing_title=title, existing_author=author)
            except ValueError as e:
                return f"({e})"

        self.title_sample_var.set(preview(self.title_pattern_var.get()))
        self.author_sample_var.set(preview(self.author_pattern_var.get()))

    # -- reordering -----------------------------------------------------

    def move_row_up(self):
        selected = self.tree.selection()
        if not selected:
            return
        row_id = selected[0]
        index = self.tree.index(row_id)
        if index > 0:
            self.tree.move(row_id, "", index - 1)
            self._update_sample()

    def move_row_down(self):
        selected = self.tree.selection()
        if not selected:
            return
        row_id = selected[0]
        index = self.tree.index(row_id)
        if index < len(self.tree.get_children()) - 1:
            self.tree.move(row_id, "", index + 1)
            self._update_sample()

    # -- adding files -----------------------------------------------------

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        folder = Path(folder)
        pdfs = sorted(f for f in folder.iterdir() if f.suffix.lower() == ".pdf")
        self._add_files(pdfs)

    def choose_files(self):
        paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        self._add_files(Path(p) for p in paths)

    def _add_files(self, paths):
        for path in paths:
            key = str(path.resolve())
            if key in self._added_paths:
                continue
            self._added_paths.add(key)

            meta_title, meta_author = read_existing_metadata(path)
            row_id = self.tree.insert(
                "", "end",
                values=(path.name, "", meta_title, "", meta_author, "pending"),
            )
            self.rows[row_id] = {"path": path}

        self._update_sample()

    # -- pattern application ------------------------------------------------

    def apply_batch_title_pattern(self):
        pattern = self.title_pattern_var.get()
        if not pattern:
            return
        for row_id in self.tree.get_children():
            self.tree.set(row_id, "title_pattern", pattern)
            self._recompute(row_id, "title_pattern", "title")

    def apply_batch_author_pattern(self):
        pattern = self.author_pattern_var.get()
        if not pattern:
            return
        for row_id in self.tree.get_children():
            self.tree.set(row_id, "author_pattern", pattern)
            self._recompute(row_id, "author_pattern", "author")

    def _recompute(self, row_id, pattern_col, target_col):
        """Re-apply the pattern in `pattern_col` for this row, writing the result into `target_col`."""
        pattern = self.tree.set(row_id, pattern_col)
        if not pattern:
            return
        path = self.rows[row_id]["path"]
        title = self.tree.set(row_id, "title")
        author = self.tree.set(row_id, "author")
        try:
            result = apply_pattern(pattern, path, existing_title=title, existing_author=author)
        except ValueError as e:
            self.log(f"{path.name}: {e}")
            return
        self.tree.set(row_id, target_col, result)

    # -- inline cell editing -------------------------------------------------

    def _on_double_click(self, event):
        if self.tree.identify("region", event.x, event.y) != "cell":
            return
        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        col_index = int(col_id[1:]) - 1
        col_name = self.tree["columns"][col_index]
        if col_name not in EDITABLE_COLUMNS:
            return

        bbox = self.tree.bbox(row_id, col_id)
        if not bbox:
            return
        x, y, width, height = bbox

        value = self.tree.set(row_id, col_name)
        entry = ttk.Entry(self.tree)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, value)
        entry.focus()
        entry.select_range(0, "end")

        def save(_event=None):
            if not entry.winfo_exists():
                return
            self.tree.set(row_id, col_name, entry.get())
            entry.destroy()
            if col_name == "title_pattern":
                self._recompute(row_id, "title_pattern", "title")
            elif col_name == "author_pattern":
                self._recompute(row_id, "author_pattern", "author")

        def cancel(_event=None):
            entry.destroy()

        entry.bind("<Return>", save)
        entry.bind("<FocusOut>", save)
        entry.bind("<Escape>", cancel)

    # -- running the batch ----------------------------------------------------

    def run_batch(self):
        row_ids = self.tree.get_children()
        total = len(row_ids)
        if total == 0:
            return

        self.run_button.configure(state="disabled")
        self.progress_bar.configure(maximum=total, value=0)

        try:
            for i, row_id in enumerate(row_ids, start=1):
                path = self.rows[row_id]["path"]
                title = self.tree.set(row_id, "title")
                author = self.tree.set(row_id, "author") or None

                self.progress_var.set(f"Processing {i} of {total}: {path.name}")
                self.update_idletasks()

                if not title:
                    self.tree.set(row_id, "status", "failed")
                    self.log(f"{path.name}: no title set, skipping")
                else:
                    result = process_file(path, title, author)
                    self.tree.set(row_id, "status", result["status"])
                    self.log(f"{path.name}: {result['message']}")

                    if result["status"] == "renamed":
                        self.rows[row_id]["path"] = result["new_path"]
                        self.tree.set(row_id, "file", result["new_path"].name)

                self.progress_bar.configure(value=i)
                self.update_idletasks()
        finally:
            self.progress_var.set(f"Done ({total} file{'s' if total != 1 else ''})")
            self.run_button.configure(state="normal")


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
