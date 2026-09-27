"""
Batch-renames PDFs and sets their /Title (and /Author) metadata using pypdf.

The core logic (process_file, apply_pattern, read_existing_metadata) has no
GUI dependencies and can be imported and used headless. Run this file
directly to launch a PySide6 (Qt) GUI for building and running a batch.

This is a refresh of pdf-renamer.py with a Qt interface, light/dark themes,
drag-and-drop, pre-run conflict checks, and a Settings dialog (conflict
handling, output folder, subfolders, sort order, starting title, theme).
Settings are saved to %APPDATA%\\PDF Renamer\\settings.ini.

Requires: pip install pypdf PySide6
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from PySide6.QtCore import QEvent, QSettings, Qt, QTimer
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QKeySequence, QPalette
from PySide6.QtWidgets import (
    QAbstractItemView, QApplication, QCheckBox, QComboBox, QDialog, QDialogButtonBox,
    QFileDialog, QFormLayout, QGridLayout, QGroupBox, QInputDialog,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMainWindow, QMessageBox,
    QPlainTextEdit, QProgressBar, QPushButton, QSizePolicy, QSpinBox, QSplitter, QTableWidget,
    QTextBrowser,
    QTableWidgetItem,
    QVBoxLayout, QWidget,
)

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


class _PaddedNumber(int):
    """An int that zero-pads itself to `pad` digits when formatted with no explicit spec."""

    def __new__(cls, value, pad):
        obj = super().__new__(cls, value)
        obj.pad = pad
        return obj

    def __format__(self, spec):
        if not spec and self.pad:
            spec = f"0{self.pad}d"
        return format(int(self), spec)


def apply_pattern(pattern, file_path, existing_title="", existing_author="", pad=0):
    """
    Substitute placeholders in `pattern`:
      {n}      - digits extracted from the file's original name, zero-padded
                 to `pad` digits (0 = no padding); an explicit spec like
                 {n:03d} overrides `pad`
      {title}  - `existing_title` (typed manually or pulled from PDF metadata)
      {author} - `existing_author` (typed manually or pulled from PDF metadata)

    Returns the resulting string. Raises ValueError if the pattern is invalid
    (e.g. an unknown placeholder, or a format spec that doesn't fit the value).
    """
    number = extract_number(Path(file_path).stem)
    try:
        return pattern.format(n=_PaddedNumber(number, pad) if number is not None else "",
                               title=existing_title, author=existing_author)
    except (KeyError, ValueError, IndexError) as e:
        raise ValueError(f"invalid pattern ({e})")


def natural_key(text):
    """Sort key that orders embedded numbers numerically ("scan2" before "scan12")."""
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", text)]


def target_path(file_path, title, output_dir=None):
    """Where `file_path` would be written for `title`, or None if the title is unusable."""
    name = sanitize_filename(title or "")
    if not name:
        return None
    folder = Path(output_dir) if output_dir else Path(file_path).parent
    return folder / f"{name}.pdf"


def unique_path(path, taken=()):
    """
    Return `path`, or "<stem> (2).pdf", "<stem> (3).pdf", ... - the first one
    that isn't on disk and whose normcase'd string isn't in `taken`.
    """
    candidate, i = path, 2
    while candidate.exists() or os.path.normcase(str(candidate)) in taken:
        candidate = path.with_name(f"{path.stem} ({i}){path.suffix}")
        i += 1
    return candidate


def check_batch(entries, on_conflict="skip", output_dir=None):
    """
    Predict what a batch will do before running it. `entries` is a list of
    (file_path, title) pairs; `on_conflict` and `output_dir` are as for
    process_file. Returns a parallel list of (status, message):
      "ready"     - will be renamed/copied as-is
      "unchanged" - file already has this name (process_file will skip it)
      "suffix"    - name is taken, a " (2)"-style number will be added
      "overwrite" - an existing file with the target name will be replaced
      "no title"  - title is empty or only invalid characters     (problem)
      "duplicate" - another entry would get the same filename      (problem)
      "exists"    - target name is taken and would be skipped, or
                    overwriting it would destroy another row's file (problem)
    """
    targets = [target_path(path, title, output_dir) for path, title in entries]

    # Windows filenames are case-insensitive, so compare normalised paths.
    def key(path):
        return os.path.normcase(str(path))

    seen = {}
    for i, target in enumerate(targets):
        if target is not None:
            seen.setdefault(key(target), []).append(i)
    sources = {key(path): i for i, (path, _) in enumerate(entries)}

    results = []
    claimed = set()  # targets already handed out, for suffix mode
    for i, ((file_path, _), target) in enumerate(zip(entries, targets)):
        if target is None:
            results.append(("no title", "title is empty or has only invalid characters"))
            continue
        if Path(file_path) == target:
            claimed.add(key(target))
            results.append(("unchanged", "already named correctly"))
            continue

        if on_conflict == "suffix":
            final = unique_path(target, claimed)
            claimed.add(key(final))
            if final == target:
                results.append(("ready", f"will be saved as {target.name}"))
            else:
                results.append(("suffix", f"{target.name} is taken; will be saved as {final.name}"))
            continue

        clashes = [j for j in seen[key(target)] if j != i]
        owner = sources.get(key(target))
        if clashes:
            rows = ", ".join(str(j + 1) for j in clashes)
            results.append(("duplicate", f"{target.name} is also the target of row {rows}"))
        elif not target.exists():
            results.append(("ready", f"will be saved as {target.name}"))
        elif on_conflict == "overwrite" and owner is not None and owner != i:
            results.append(("exists", f"{target.name} is row {owner + 1}'s original file; "
                                       "overwriting it would destroy that file"))
        elif on_conflict == "overwrite":
            results.append(("overwrite", f"will replace the existing {target.name}"))
        else:
            results.append(("exists", f"{target.name} already exists in that folder"))
    return results


def process_file(file_path, title, author=None, on_conflict="skip", output_dir=None):
    """
    Save `file_path` as "<title>.pdf" and set the PDF's /Title (and /Author,
    if given) metadata.

    output_dir:  None renames the file in place (the original is replaced);
                 a folder writes a renamed copy there and keeps the original.
    on_conflict: what to do if the target name is already taken -
                 "skip", "suffix" (save as "<title> (2).pdf" etc.), or "overwrite".

    Does not raise on failure; every outcome is reported via the returned
    dict so a batch loop can continue past errors:
        {"status": "renamed" | "copied" | "skipped" | "failed",
         "message": str, "old_path": Path, "new_path": Path or None}
    """
    old_path = Path(file_path)
    new_path = target_path(old_path, title, output_dir)
    if new_path is None:
        return {"status": "failed", "message": "empty/invalid title",
                "old_path": old_path, "new_path": None}

    if old_path == new_path:
        return {"status": "skipped", "message": "already named correctly",
                "old_path": old_path, "new_path": new_path}

    note = ""
    if new_path.exists():
        if on_conflict == "suffix":
            new_path = unique_path(new_path)
        elif on_conflict == "overwrite" and not os.path.samefile(old_path, new_path):
            note = " (replaced existing file)"
        else:
            return {"status": "skipped", "message": f"target {new_path.name} already exists",
                    "old_path": old_path, "new_path": new_path}

    # Write to a temp file first so a failure never leaves a half-written PDF
    # (or a clobbered one, in overwrite mode) at the target name.
    tmp_path = new_path.with_name(f".{new_path.name}.tmp")
    try:
        reader = PdfReader(str(old_path))
        writer = PdfWriter()
        writer.append(reader)

        metadata = {"/Title": title}
        if author:
            metadata["/Author"] = author
        writer.add_metadata(metadata)

        with open(tmp_path, "wb") as f:
            writer.write(f)
        os.replace(tmp_path, new_path)

        if output_dir is None:
            os.remove(old_path)
            status = "renamed"
        else:
            status = "copied"
        return {"status": status, "message": f"{old_path.name} -> {new_path}{note}"
                if output_dir else f"{old_path.name} -> {new_path.name}{note}",
                "old_path": old_path, "new_path": new_path}

    except Exception as e:
        if tmp_path.exists():
            tmp_path.unlink()
        return {"status": "failed", "message": str(e), "old_path": old_path, "new_path": None}


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

COLUMNS = ("file", "title_pattern", "title", "author_pattern", "author", "status")
HEADINGS = ("File", "Title Pattern", "Title", "Author Pattern", "Author", "Status")
COL = {name: i for i, name in enumerate(COLUMNS)}
EDITABLE_COLUMNS = ("title_pattern", "title", "author_pattern", "author")
PATH_ROLE = Qt.ItemDataRole.UserRole
EDIT_TRIGGERS = (QAbstractItemView.EditTrigger.DoubleClicked
                 | QAbstractItemView.EditTrigger.EditKeyPressed)
QWIDGETSIZE_MAX = 16777215  # Qt's "no maximum size" value
BATCH_PANEL_WIDTH = 340
DEFAULT_COLUMN_WIDTHS =(180, 150, 200, 150, 140, 90)  # in COLUMNS order
TITLE_MIN_WIDTH = 200
PROBLEM_STATUSES = ("no title", "duplicate", "exists")
# Status text -> theme color key; anything unlisted uses "muted".
STATUS_COLORS = {
    "renamed": "renamed", "copied": "renamed", "skipped": "skipped", "failed": "failed",
    "unchanged": "skipped", "suffix": "skipped", "overwrite": "skipped",
    **{s: "failed" for s in PROBLEM_STATUSES},
}

# User preferences edited in the Settings dialog: key -> default.
DEFAULT_PREFS = {
    "on_conflict": "skip",        # skip | suffix | overwrite
    "output_mode": "in_place",    # in_place | copy
    "output_dir": "",             # used when output_mode == "copy"
    "include_subfolders": False,
    "sort_order": "natural",      # natural | name | modified
    "initial_title": "metadata",  # metadata | filename | blank
    "theme": "system",            # system | light | dark
}
# (value, label) choices for each combo-box preference.
PREF_CHOICES = {
    "on_conflict": (("skip", "Skip the file"),
                    ("suffix", 'Add a number, e.g. "Title (2).pdf"'),
                    ("overwrite", "Overwrite the existing file")),
    "output_mode": (("in_place", "Rename in place (replaces the originals)"),
                    ("copy", "Save renamed copies to an output folder")),
    "sort_order": (("natural", "Name, numbers in order (2 before 10)"),
                   ("name", "Name, alphabetical (10 before 2)"),
                   ("modified", "Date modified, oldest first")),
    "initial_title": (("metadata", "The PDF's existing Title metadata"),
                      ("filename", "The filename (without .pdf)"),
                      ("blank", "Blank")),
    "theme": (("system", "Follow system"), ("light", "Light"), ("dark", "Dark")),
}

THEMES = {
    "light": {
        "window": "#f3f3f3", "base": "#ffffff", "alt": "#f7f7f7", "text": "#1a1a1a",
        "muted": "#6b6b6b", "button": "#fbfbfb", "border": "#d6d6d6",
        "header": "#ebebeb", "header_hover": "#dedede", "divider": "#a0a0a0",
        "accent": "#005fb8", "accent_hover": "#1a6fc0", "accent_text": "#ffffff",
        "renamed": "#107c10", "skipped": "#9d5d00", "failed": "#c42b1c",
        # 3D bevels: "shade"/"shade_deep" for shadowed edges, "light_edge" for lit edges
        "well": "#eaeaea", "shade": "#a8a8a8", "shade_deep": "#8a8a8a", "light_edge": "#ffffff",
        "btn_top": "#ffffff", "btn_bottom": "#e4e4e4", "btn_hover_top": "#ffffff",
        "btn_hover_bottom": "#eaf2fb", "btn_pressed": "#d6d6d6",
        "accent_top": "#2a80d6", "accent_bottom": "#004f9a", "accent_pressed": "#00437f",
        "accent_light": "#6aa8e6", "accent_dark": "#00335f",
    },
    "dark": {
        "window": "#202020", "base": "#1c1c1c", "alt": "#262626", "text": "#e0e0e0",
        "muted": "#9a9a9a", "button": "#2d2d2d", "border": "#3a3a3a",
        "header": "#2b2b2b", "header_hover": "#363636", "divider": "#5c5c5c",
        "accent": "#4cc2ff", "accent_hover": "#6ccdff", "accent_text": "#000000",
        "renamed": "#6ccb5f", "skipped": "#fce100", "failed": "#ff99a4",
        "well": "#272727", "shade": "#0b0b0b", "shade_deep": "#000000", "light_edge": "#4a4a4a",
        "btn_top": "#3c3c3c", "btn_bottom": "#2a2a2a", "btn_hover_top": "#464646",
        "btn_hover_bottom": "#313131", "btn_pressed": "#202020",
        "accent_top": "#86d7ff", "accent_bottom": "#38aae8", "accent_pressed": "#2b93cc",
        "accent_light": "#b5e7ff", "accent_dark": "#1c75a6",
    },
}

STYLESHEET = """
QLabel#Heading {{ font-size: 16pt; font-weight: 600; }}
QLabel#Muted, QLabel#Sample {{ color: {muted}; }}
QLabel#Issues {{ color: {failed}; font-weight: 600; }}
QLabel#Section {{ font-weight: 600; }}

/* Group boxes: recessed panels (shadow on top/left, light on bottom/right) */
QGroupBox {{
    background: {well}; border: 1px solid; border-color: {shade} {light_edge} {light_edge} {shade};
    border-radius: 6px; margin-top: 14px; padding: 12px 10px 10px 10px; font-weight: 600;
}}
QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 4px; }}
QGroupBox QLabel, QGroupBox QPushButton, QGroupBox QLineEdit,
QGroupBox QCheckBox, QGroupBox QComboBox {{ font-weight: normal; }}

/* Inputs, table, log and help text: sunken wells with a deeper top/left bevel */
QLineEdit, QPlainTextEdit, QTextBrowser, QTableWidget {{
    background: {base}; border-style: solid; border-width: 2px 1px 1px 2px;
    border-color: {shade_deep} {light_edge} {light_edge} {shade_deep}; border-radius: 4px;
}}
QLineEdit {{ padding: 3px 6px; }}
QLineEdit:focus {{ border-color: {accent}; }}
QLineEdit:disabled {{ color: {muted}; border-color: {shade} {well} {well} {shade}; }}
QAbstractSpinBox QLineEdit, QAbstractSpinBox QLineEdit:focus {{
    padding: 0; border: none; background: transparent;
}}

/* Buttons: raised (lit top/left, thicker shadow bottom/right); pressing flips the
   bevel so the button visibly sinks, and the label shifts down-right by 1px */
QPushButton {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {btn_top}, stop:1 {btn_bottom});
    border-style: solid; border-width: 1px 2px 2px 1px;
    border-color: {light_edge} {shade_deep} {shade_deep} {light_edge};
    border-radius: 4px; padding: 5px 12px;
}}
QPushButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {btn_hover_top}, stop:1 {btn_hover_bottom});
}}
QPushButton:pressed {{
    background: {btn_pressed}; border-width: 2px 1px 1px 2px;
    border-color: {shade_deep} {light_edge} {light_edge} {shade_deep};
}}
QPushButton:disabled {{
    color: {muted}; background: {well}; border-width: 1px;
    border-color: {shade} {shade} {shade} {shade};
}}
QPushButton#Accent {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {accent_top}, stop:1 {accent_bottom});
    color: {accent_text}; border-color: {accent_light} {accent_dark} {accent_dark} {accent_light};
    font-weight: 600; padding: 5px 28px;
}}
QPushButton#Accent:hover {{ background: {accent_hover}; }}
QPushButton#Accent:pressed {{
    background: {accent_pressed}; border-color: {accent_dark} {accent_light} {accent_light} {accent_dark};
}}
QPushButton#Accent:disabled {{ background: {well}; border-color: {shade}; color: {muted}; }}
QPushButton#Chip {{ padding: 3px 8px; font-family: Consolas; }}

/* Table headings: raised, with a lit left edge beside each divider for a ridged look */
QHeaderView::section {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {btn_top}, stop:1 {header});
    border: none; border-top: 1px solid {light_edge}; border-left: 1px solid {light_edge};
    border-bottom: 1px solid {divider}; border-right: 1px solid {divider};
    padding: 5px 6px; font-weight: 600;
}}
QHeaderView::section:hover {{ background: {header_hover}; }}

QProgressBar {{
    background: {base}; border-style: solid; border-width: 2px 1px 1px 2px;
    border-color: {shade_deep} {light_edge} {light_edge} {shade_deep}; border-radius: 4px;
    max-height: 10px;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {accent_top}, stop:1 {accent_bottom});
    border-radius: 2px;
}}
QPlainTextEdit {{ font-family: Consolas; font-size: 9pt; }}
QSplitter::handle:vertical {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 transparent, stop:0.34 transparent,
        stop:0.35 {divider}, stop:0.65 {divider}, stop:0.66 transparent, stop:1 transparent);
}}
QSplitter::handle:vertical:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 transparent, stop:0.24 transparent,
        stop:0.25 {accent}, stop:0.75 {accent}, stop:0.76 transparent, stop:1 transparent);
}}
QSplitter::handle:vertical:disabled {{ background: transparent; }}
"""


class SettingsDialog(QDialog):
    """Edits a copy of the app's preferences; read the result from values() after exec()."""

    def __init__(self, prefs, parent=None, on_reset_columns=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(560)
        self.combos = {}
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        renaming = QGroupBox("Renaming")
        form = QFormLayout(renaming)
        form.addRow("If the new name is taken:", self._combo("on_conflict"))
        form.addRow("Save renamed files:", self._combo("output_mode"))
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("Choose a folder...")
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self._browse_output_dir)
        folder_row = QHBoxLayout()
        folder_row.addWidget(self.output_dir_edit, 1)
        folder_row.addWidget(self.browse_button)
        form.addRow("Output folder:", folder_row)
        self.combos["output_mode"].currentIndexChanged.connect(self._update_enabled)
        layout.addWidget(renaming)

        adding = QGroupBox("Adding Files")
        form = QFormLayout(adding)
        self.subfolders_check = QCheckBox("Include subfolders when adding a folder")
        form.addRow(self.subfolders_check)
        form.addRow("Sort new files by:", self._combo("sort_order"))
        form.addRow("Starting title:", self._combo("initial_title"))
        layout.addWidget(adding)

        appearance = QGroupBox("Appearance")
        form = QFormLayout(appearance)
        form.addRow("Theme:", self._combo("theme"))
        if on_reset_columns is not None:
            # Takes effect immediately (like a layout reset), independent of OK/Cancel.
            reset_columns = QPushButton("Reset Column Widths")
            reset_columns.setToolTip("Put the file list's columns back to their default widths.")
            reset_done = QLabel()
            reset_done.setObjectName("Muted")

            def do_reset():
                on_reset_columns()
                reset_done.setText("Column widths reset.")

            reset_columns.clicked.connect(do_reset)
            reset_row = QHBoxLayout()
            reset_row.addWidget(reset_columns)
            reset_row.addWidget(reset_done, 1)
            form.addRow("File list:", reset_row)
        layout.addWidget(appearance)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                   | QDialogButtonBox.StandardButton.Cancel
                                   | QDialogButtonBox.StandardButton.RestoreDefaults)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(
            lambda: self._set_values(DEFAULT_PREFS))
        layout.addWidget(buttons)

        self._set_values(prefs)

    def _combo(self, pref):
        combo = QComboBox()
        for value, label in PREF_CHOICES[pref]:
            combo.addItem(label, value)
        self.combos[pref] = combo
        return combo

    def _set_values(self, prefs):
        for pref, combo in self.combos.items():
            combo.setCurrentIndex(max(0, combo.findData(prefs[pref])))
        self.output_dir_edit.setText(prefs["output_dir"])
        self.subfolders_check.setChecked(prefs["include_subfolders"])
        self._update_enabled()

    def _update_enabled(self):
        copy_mode = self.combos["output_mode"].currentData() == "copy"
        self.output_dir_edit.setEnabled(copy_mode)
        self.browse_button.setEnabled(copy_mode)

    def _browse_output_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "Output Folder", self.output_dir_edit.text())
        if folder:
            self.output_dir_edit.setText(folder)

    def values(self):
        prefs = {pref: combo.currentData() for pref, combo in self.combos.items()}
        prefs["output_dir"] = self.output_dir_edit.text().strip()
        prefs["include_subfolders"] = self.subfolders_check.isChecked()
        return prefs

    def accept(self):
        if self.combos["output_mode"].currentData() == "copy" and not self.output_dir_edit.text().strip():
            QMessageBox.warning(self, "Output folder needed",
                                "Choose an output folder, or switch back to renaming in place.")
            return
        super().accept()


class HelpDialog(QDialog):
    """Renders HELP.md (bundled next to the script / inside the .exe)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PDF Renamer Help")
        self.resize(780, 680)
        layout = QVBoxLayout(self)
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        help_file = resource_path("HELP.md")
        try:
            browser.setMarkdown(help_file.read_text(encoding="utf-8"))
        except OSError:
            browser.setPlainText(f"The help file could not be found.\n\nExpected it at:\n{help_file}")
        layout.addWidget(browser)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.close)
        layout.addWidget(buttons)


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Renamer")
        self.resize(1000, 700)
        self.setAcceptDrops(True)

        self.theme = "light"  # the theme actually shown; prefs["theme"] may be "system"
        self.prefs = dict(DEFAULT_PREFS)
        self.last_dir = ""  # starting folder for the Add Folder/Files dialogs
        self._help_window = None  # created on first use
        self._added_paths = set()  # resolved path strings, to avoid duplicates
        self._updating = False  # suppresses itemChanged handling for programmatic edits

        # Saved as %APPDATA%\PDF Renamer\settings.ini on Windows.
        self.settings = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope,
                                  "PDF Renamer", "settings")

        self._build_widgets()
        self._build_shortcuts()
        self._load_settings()
        self.apply_theme()
        self._validate()  # fills in the file count and problem summary
        self._update_sample()
        QApplication.styleHints().colorSchemeChanged.connect(self._on_system_theme_changed)

    # -- settings ---------------------------------------------------------------

    def _load_settings(self):
        s = self.settings
        if s.value("window/geometry"):
            self.restoreGeometry(s.value("window/geometry"))
        try:  # INI files hand lists back as strings
            sizes = [int(v) for v in s.value("window/log_sizes") or []]
        except (TypeError, ValueError):
            sizes = []
        if len(sizes) == 2 and min(sizes) > 0:
            self.splitter.setSizes(sizes)
        if s.value("window/log_hidden", False, type=bool):
            self.set_log_hidden(True)
            self._log_sizes = sizes if len(sizes) == 2 and min(sizes) > 0 else None
        if s.value("window/columns"):
            self.table.horizontalHeader().restoreState(s.value("window/columns"))
            # Older saved states have Title in Stretch mode; sizing is now manual.
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.title_width = max(TITLE_MIN_WIDTH, s.value("window/title_width", TITLE_MIN_WIDTH, type=int))
        self._fit_title_column()
        for pref, default in DEFAULT_PREFS.items():
            value = s.value(f"prefs/{pref}", default, type=type(default))
            valid = [v for v, _ in PREF_CHOICES[pref]] if pref in PREF_CHOICES else None
            self.prefs[pref] = value if valid is None or value in valid else default
        old_theme = s.value("appearance/theme", "", type=str)  # pre-Settings-dialog key
        if not s.contains("prefs/theme") and old_theme in THEMES:
            self.prefs["theme"] = old_theme
        if self.prefs["output_mode"] == "copy" and not self.prefs["output_dir"]:
            self.prefs["output_mode"] = "in_place"
        self.title_pattern_edit.setText(s.value("patterns/title", "", type=str))
        self.author_pattern_edit.setText(s.value("patterns/author", "", type=str))
        self.pad_spin.setValue(s.value("patterns/pad_digits", 0, type=int))
        self.last_dir = s.value("paths/last_dir", "", type=str)
        self._load_presets()

    def _save_settings(self):
        s = self.settings
        s.setValue("window/geometry", self.saveGeometry())
        s.remove("window/splitter")  # superseded by window/log_sizes
        self._save_layout()
        s.remove("appearance")  # pre-Settings-dialog theme key, now prefs/theme
        for pref, value in self.prefs.items():
            s.setValue(f"prefs/{pref}", value)
        s.setValue("patterns/title", self.title_pattern_edit.text())
        s.setValue("patterns/author", self.author_pattern_edit.text())
        s.setValue("patterns/pad_digits", self.pad_spin.value())
        s.setValue("paths/last_dir", self.last_dir)
        s.sync()

    def closeEvent(self, event):
        self._save_settings()
        super().closeEvent(event)

    # -- layout ---------------------------------------------------------------

    def _build_widgets(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 12, 16, 16)
        root.setSpacing(10)

        # Header
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        heading = QLabel("PDF Renamer")
        heading.setObjectName("Heading")
        subtitle = QLabel("Add PDFs (or drag them onto the window), set naming patterns, then Run.")
        subtitle.setObjectName("Muted")
        title_box.addWidget(heading)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()
        self.theme_button = QPushButton("Dark Mode")
        self.theme_button.clicked.connect(self.toggle_theme)
        header.addWidget(self.theme_button, alignment=Qt.AlignmentFlag.AlignTop)
        settings_button = QPushButton("⚙ Settings")
        settings_button.setToolTip("Settings (Ctrl+,)")
        settings_button.clicked.connect(self.open_settings)
        header.addWidget(settings_button, alignment=Qt.AlignmentFlag.AlignTop)
        help_button = QPushButton("? Help")
        help_button.setToolTip("How to use PDF Renamer (F1)")
        help_button.clicked.connect(self.show_help)
        header.addWidget(help_button, alignment=Qt.AlignmentFlag.AlignTop)
        root.addLayout(header)

        # Naming patterns
        pattern_box = QGroupBox("Naming Patterns")
        grid = QGridLayout(pattern_box)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(6)

        self.title_pattern_edit = QLineEdit()
        self.title_pattern_edit.setPlaceholderText("e.g. Chapter {n} - {title}")
        self.author_pattern_edit = QLineEdit()
        self.author_pattern_edit.setPlaceholderText("e.g. {author}")
        self.title_sample = QLabel()
        self.author_sample = QLabel()
        for label in (self.title_sample, self.author_sample):
            label.setObjectName("Sample")
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        title_apply = QPushButton("Apply to All")
        title_apply.clicked.connect(self.apply_batch_title_pattern)
        author_apply = QPushButton("Apply to All")
        author_apply.clicked.connect(self.apply_batch_author_pattern)

        # Presets: saved title/author/padding combinations
        self.presets = {}  # name -> {"title": str, "author": str, "pad": int}
        self._loading_preset = False  # True while a chosen preset fills the fields
        self.preset_combo = QComboBox()
        self.preset_combo.setMinimumWidth(240)
        self.preset_combo.setToolTip("Load a saved set of patterns into the fields below")
        self.preset_combo.activated.connect(self._on_preset_chosen)
        save_preset = QPushButton("Save as Preset...")
        save_preset.setToolTip("Save the current title pattern, author pattern and padding under a name")
        save_preset.clicked.connect(self.save_preset)
        self.delete_preset_button = QPushButton("Delete")
        self.delete_preset_button.setToolTip("Delete the selected preset")
        self.delete_preset_button.clicked.connect(self.delete_preset)
        preset_row = QHBoxLayout()
        preset_row.setSpacing(6)
        preset_row.addWidget(self.preset_combo)
        preset_row.addWidget(save_preset)
        preset_row.addWidget(self.delete_preset_button)
        preset_row.addStretch()

        grid.addWidget(QLabel("Preset:"), 0, 0)
        grid.addLayout(preset_row, 0, 1, 1, 2)
        grid.setRowMinimumHeight(1, 2)  # empty spacer row: separates presets from the fields
        grid.addWidget(QLabel("Title pattern:"), 2, 0)
        grid.addWidget(self.title_pattern_edit, 2, 1)
        grid.addWidget(title_apply, 2, 2)
        grid.addWidget(self.title_sample, 3, 1, 1, 2)
        grid.addWidget(QLabel("Author pattern:"), 4, 0)
        grid.addWidget(self.author_pattern_edit, 4, 1)
        grid.addWidget(author_apply, 4, 2)
        grid.addWidget(self.author_sample, 5, 1, 1, 2)
        grid.setColumnStretch(1, 1)

        chips = QHBoxLayout()
        chips.setSpacing(4)
        chips.addWidget(QLabel("Insert into focused field:"))
        for placeholder in ("{n}", "{title}", "{author}"):
            chip = QPushButton(placeholder)
            chip.setObjectName("Chip")
            chip.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # keep focus in the pattern field
            chip.clicked.connect(lambda _=False, p=placeholder: self._insert_placeholder(p))
            chips.addWidget(chip)
        chips.addSpacing(24)
        chips.addWidget(QLabel("Pad {n} with leading zeros to:"))
        self.pad_spin = QSpinBox()
        self.pad_spin.setRange(0, 10)
        self.pad_spin.setSpecialValueText("Off")
        self.pad_spin.setSuffix(" digits")
        # Fusion sizes spin boxes too short for Segoe UI 10pt, clipping descenders;
        # match the height of the styled line edits instead.
        self.pad_spin.setMinimumSize(100, 28)
        self.pad_spin.setToolTip("Zero-pad the number from the filename, e.g. 3 digits: 7 → 007.\n"
                                 "An explicit format like {n:02d} in a pattern overrides this.")
        self.pad_spin.valueChanged.connect(self._on_pad_changed)
        chips.addWidget(self.pad_spin)
        chips.addStretch()
        grid.addLayout(chips, 6, 0, 1, 3)

        self._active_pattern_edit = self.title_pattern_edit
        QApplication.instance().focusChanged.connect(self._on_focus_changed)
        self.title_pattern_edit.textChanged.connect(self._update_sample)
        self.author_pattern_edit.textChanged.connect(self._update_sample)
        # Editing the fields away from the loaded preset deselects it.
        self.title_pattern_edit.textChanged.connect(self._sync_preset_selection)
        self.author_pattern_edit.textChanged.connect(self._sync_preset_selection)
        self.pad_spin.valueChanged.connect(self._sync_preset_selection)

        # Batch panel: sits beside the patterns, holding everything that acts on the whole batch
        batch_box = QGroupBox("Batch")
        batch_box.setFixedWidth(BATCH_PANEL_WIDTH)
        batch = QVBoxLayout(batch_box)
        batch.setSpacing(8)
        batch_buttons = QGridLayout()
        batch_buttons.setHorizontalSpacing(6)
        batch_buttons.setVerticalSpacing(6)
        for i, (text, tip, slot) in enumerate((
            ("Add Folder...", "Add every PDF in a folder (Ctrl+Shift+O)", self.choose_folder),
            ("Add Files...", "Add individual PDFs (Ctrl+O)", self.choose_files),
            ("Clear List", "Remove all files from the list", self.clear_file_list),
            ("Reset", "Clear the list, patterns and log", self.reset_app),
        )):
            btn = QPushButton(text)
            btn.setToolTip(tip)
            btn.clicked.connect(slot)
            batch_buttons.addWidget(btn, i // 2, i % 2)
        batch.addLayout(batch_buttons)
        batch.addStretch()
        self.run_button = QPushButton("Run")
        self.run_button.setObjectName("Accent")
        self.run_button.setMinimumHeight(40)
        self.run_button.setToolTip("Rename all files (Ctrl+Enter)")
        self.run_button.clicked.connect(self.run_batch)
        batch.addWidget(self.run_button)
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setValue(0)
        batch.addWidget(self.progress_bar)
        self.progress_label = QLabel()
        self.progress_label.setObjectName("Muted")
        # Long "Processing ... <filename>" text is elided to fit rather than widening the panel.
        self.progress_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        batch.addWidget(self.progress_label)
        self.issue_label = QLabel()
        self.issue_label.setObjectName("Issues")
        batch.addWidget(self.issue_label)
        self._set_progress("Ready")

        top_row = QHBoxLayout()
        top_row.setSpacing(12)
        top_row.addWidget(pattern_box, 1)
        top_row.addWidget(batch_box)
        root.addLayout(top_row)

        # File list bar: count on the left, per-row actions on the right
        files_bar = QHBoxLayout()
        files_bar.setSpacing(6)
        files_heading = QLabel("Files")
        files_heading.setObjectName("Section")
        self.file_count_label = QLabel()
        self.file_count_label.setObjectName("Muted")
        files_bar.addWidget(files_heading)
        files_bar.addWidget(self.file_count_label)
        files_bar.addStretch()
        for text, tip, slot in (
            ("Move Up", "Move the selected file up (Alt+Up)", self.move_row_up),
            ("Move Down", "Move the selected file down (Alt+Down)", self.move_row_down),
            ("Remove", "Remove the selected file from the list (Delete)", self.remove_selected_row),
        ):
            btn = QPushButton(text)
            btn.setToolTip(tip)
            btn.clicked.connect(slot)
            files_bar.addWidget(btn)
        root.addLayout(files_bar)

        # Table + log, resizable against each other
        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(HEADINGS)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(EDIT_TRIGGERS)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        for col, width in zip(COLUMNS, DEFAULT_COLUMN_WIDTHS):
            self.table.setColumnWidth(COL[col], width)
        # Title fills the spare width but never shrinks below TITLE_MIN_WIDTH (a plain
        # Stretch column collapses on narrow windows); past that the table scrolls.
        self.table.horizontalHeader().setDefaultAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.title_width = TITLE_MIN_WIDTH  # Title's minimum; raised by dragging it wider
        self._fitting = False  # True while _fit_title_column resizes Title itself
        # Save column widths shortly after a drag ends, not only when the app closes.
        self._layout_save_timer = QTimer(self, singleShot=True, interval=500)
        self._layout_save_timer.timeout.connect(self._save_layout)
        self.table.horizontalHeader().sectionResized.connect(self._on_section_resized)
        self.table.viewport().installEventFilter(self)
        self.table.itemChanged.connect(self._on_item_changed)

        self.log_box = QGroupBox("Log")
        log_layout = QVBoxLayout(self.log_box)
        log_bar = QHBoxLayout()
        self.log_toggle_button = QPushButton("Hide Log")
        self.log_toggle_button.setToolTip("Collapse the log to give the file list more room")
        self.log_toggle_button.clicked.connect(lambda: self.set_log_hidden(not self.log_hidden))
        log_bar.addWidget(self.log_toggle_button)
        self.log_resize_hint = QLabel("Drag the line above the log to resize it.")
        self.log_resize_hint.setObjectName("Muted")
        log_bar.addWidget(self.log_resize_hint)
        log_bar.addStretch()
        self.clear_log_button = QPushButton("Clear")
        self.clear_log_button.clicked.connect(lambda: self.log_text.clear())
        self.export_log_button = QPushButton("Export Log...")
        self.export_log_button.setToolTip("Save the log to a text file (Ctrl+Shift+E)")
        self.export_log_button.clicked.connect(self.export_log)
        log_bar.addWidget(self.clear_log_button)
        log_bar.addWidget(self.export_log_button)
        log_layout.addLayout(log_bar)
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(60)
        self.log_text.textChanged.connect(self._update_log_buttons)
        log_layout.addWidget(self.log_text)
        self.log_hidden = False
        self._log_sizes = None  # splitter sizes to restore when the log is shown again
        self.log_box.installEventFilter(self)  # see eventFilter: keeps a collapsed log fitted

        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.addWidget(self.table)
        self.splitter.addWidget(self.log_box)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(10)
        self.splitter.splitterMoved.connect(lambda *_: self._layout_save_timer.start())
        root.addWidget(self.splitter, 1)
        self._update_log_buttons()

    def _build_shortcuts(self):
        for keys, slot in (
            (QKeySequence.StandardKey.Open, self.choose_files),
            ("Ctrl+Shift+O", self.choose_folder),
            ("Ctrl+Return", self.run_batch),
            ("Alt+Up", self.move_row_up),
            ("Alt+Down", self.move_row_down),
            ("Ctrl+,", self.open_settings),
            ("Ctrl+Shift+E", self.export_log),
            (QKeySequence.StandardKey.HelpContents, self.show_help),  # F1
        ):
            action = QAction(self)
            action.setShortcut(QKeySequence(keys))
            action.triggered.connect(slot)
            self.addAction(action)

        delete = QAction(self.table)
        delete.setShortcut(QKeySequence(QKeySequence.StandardKey.Delete))
        delete.setShortcutContext(Qt.ShortcutContext.WidgetShortcut)
        delete.triggered.connect(self.remove_selected_row)
        self.table.addAction(delete)

    def log(self, message):
        self.log_text.appendPlainText(f"[{datetime.now():%H:%M:%S}] {message}")

    def _set_progress(self, text):
        """Show `text` under the progress bar, shortened with "..." if the panel is too narrow."""
        self._progress_text = text
        label = self.progress_label
        width = label.width() if label.isVisible() else BATCH_PANEL_WIDTH // 2
        label.setText(label.fontMetrics().elidedText(text, Qt.TextElideMode.ElideMiddle, width))
        label.setToolTip(text if label.text() != text else "")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "_progress_text"):
            self._set_progress(self._progress_text)  # re-fit to the label's new width

    # -- log panel ----------------------------------------------------------------

    def _update_log_buttons(self):
        has_text = bool(self.log_text.toPlainText())
        self.clear_log_button.setEnabled(has_text)
        self.export_log_button.setEnabled(has_text)

    def set_log_hidden(self, hidden):
        """Collapse the log to its button bar (or expand it again)."""
        if hidden == self.log_hidden:
            return
        self.log_hidden = hidden
        if hidden:
            self._log_sizes = self.splitter.sizes()
            self.log_text.hide()
            self._fit_collapsed_log()
        else:
            self.log_box.setMaximumHeight(QWIDGETSIZE_MAX)
            self.log_text.show()
            if self._log_sizes:
                self.splitter.setSizes(self._log_sizes)
        self.log_resize_hint.setVisible(not hidden)
        self.splitter.handle(1).setEnabled(not hidden)
        self.log_toggle_button.setText("Show Log" if hidden else "Hide Log")
        self._layout_save_timer.start()

    def _fit_collapsed_log(self):
        """
        Size the collapsed log to exactly its button bar. Must be re-run whenever the
        stylesheet changes: the bar's height depends on button padding/borders, and a
        height measured before styling (e.g. restoring a hidden log at startup) is too
        small and squashes the buttons.
        """
        if self.log_hidden:
            needed = self.log_box.minimumSizeHint().height()
            if self.log_box.maximumHeight() != needed:
                self.log_box.setMaximumHeight(needed)

    def export_log(self):
        text = self.log_text.toPlainText()
        if not text:
            return
        default = Path(self.last_dir or Path.home()) / f"PDF Renamer log {datetime.now():%Y-%m-%d %H%M}.txt"
        path, _ = QFileDialog.getSaveFileName(self, "Export Log", str(default),
                                              "Text files (*.txt);;All files (*)")
        if not path:
            return
        try:
            Path(path).write_text(text + "\n", encoding="utf-8")
        except OSError as e:
            QMessageBox.warning(self, "Export failed", f"Couldn't save the log:\n{e}")
            return
        self.log(f"Log exported to {path}")

    # -- title column sizing ------------------------------------------------------

    def eventFilter(self, obj, event):
        if obj is self.table.viewport() and event.type() == QEvent.Type.Resize:
            self._fit_title_column()
        elif obj is self.log_box and event.type() == QEvent.Type.LayoutRequest:
            # The log's contents changed size (e.g. the stylesheet was applied or
            # switched), so a collapsed log needs re-fitting to its button bar.
            self._fit_collapsed_log()
        return super().eventFilter(obj, event)

    def _on_section_resized(self, index, _old, new):
        if self._fitting:
            return
        if index == COL["title"]:
            # A manual drag on Title sets the width it should keep from now on.
            self.title_width = max(TITLE_MIN_WIDTH, new)
        self._fit_title_column()
        self._layout_save_timer.start()

    def _fit_title_column(self):
        header = self.table.horizontalHeader()
        others = sum(header.sectionSize(i) for i in range(len(COLUMNS)) if i != COL["title"])
        width = max(self.title_width, self.table.viewport().width() - others)
        if header.sectionSize(COL["title"]) != width:
            self._fitting = True
            try:
                header.resizeSection(COL["title"], width)
            finally:
                self._fitting = False

    def reset_column_widths(self):
        """Put every column back to its default width and save that immediately."""
        self._fitting = True  # these are programmatic, not user drags
        try:
            for col, width in zip(COLUMNS, DEFAULT_COLUMN_WIDTHS):
                self.table.setColumnWidth(COL[col], width)
        finally:
            self._fitting = False
        self.title_width = TITLE_MIN_WIDTH
        self._fit_title_column()
        self._layout_save_timer.stop()
        self._save_layout()

    def _save_layout(self):
        """Save column widths and log size/visibility (called shortly after they change)."""
        s = self.settings
        s.setValue("window/columns", self.table.horizontalHeader().saveState())
        s.setValue("window/title_width", self.title_width)
        # While the log is collapsed, remember the expanded sizes rather than the collapsed ones.
        s.setValue("window/log_sizes", self._log_sizes if self.log_hidden else self.splitter.sizes())
        s.setValue("window/log_hidden", self.log_hidden)
        s.sync()

    def show_help(self):
        """Show HELP.md in a non-modal window, so it can stay open while you work."""
        if self._help_window is None:
            self._help_window = HelpDialog(self)
        self._help_window.show()
        self._help_window.raise_()
        self._help_window.activateWindow()

    def open_settings(self):
        dialog = SettingsDialog(self.prefs, self, on_reset_columns=self.reset_column_widths)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.prefs = dialog.values()
        self._save_settings()
        self.apply_theme()
        self._validate()

    def _output_dir(self):
        """Folder renamed copies go to, or None when renaming in place."""
        if self.prefs["output_mode"] == "copy" and self.prefs["output_dir"]:
            return Path(self.prefs["output_dir"])
        return None

    # -- theme ------------------------------------------------------------------

    def toggle_theme(self):
        # An explicit toggle stops following the system theme.
        self.prefs["theme"] = "dark" if self.theme == "light" else "light"
        self.apply_theme()

    def _on_system_theme_changed(self):
        if self.prefs["theme"] == "system":
            self.apply_theme()

    def apply_theme(self):
        if self.prefs["theme"] == "system":
            dark = QApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark
            self.theme = "dark" if dark else "light"
        else:
            self.theme = self.prefs["theme"]
        c = THEMES[self.theme]
        palette = QPalette()
        for role, key in (
            (QPalette.ColorRole.Window, "window"), (QPalette.ColorRole.WindowText, "text"),
            (QPalette.ColorRole.Base, "base"), (QPalette.ColorRole.AlternateBase, "alt"),
            (QPalette.ColorRole.Text, "text"), (QPalette.ColorRole.Button, "button"),
            (QPalette.ColorRole.ButtonText, "text"), (QPalette.ColorRole.PlaceholderText, "muted"),
            (QPalette.ColorRole.Highlight, "accent"), (QPalette.ColorRole.HighlightedText, "accent_text"),
            (QPalette.ColorRole.ToolTipBase, "base"), (QPalette.ColorRole.ToolTipText, "text"),
        ):
            palette.setColor(role, QColor(c[key]))
        app = QApplication.instance()
        app.setPalette(palette)
        app.setStyleSheet(STYLESHEET.format(**c))
        self.theme_button.setText("Light Mode" if self.theme == "dark" else "Dark Mode")
        for row in range(self.table.rowCount()):
            self._color_status(row)

    def _color_status(self, row):
        item = self.table.item(row, COL["status"])
        if item is None:
            return
        colors = THEMES[self.theme]
        self._updating = True
        try:
            item.setForeground(QColor(colors[STATUS_COLORS.get(item.text(), "muted")]))
            # Flag the title itself too, so the offending value stands out.
            title_item = self.table.item(row, COL["title"])
            if item.text() in PROBLEM_STATUSES:
                title_item.setForeground(QColor(colors["failed"]))
            else:
                title_item.setData(Qt.ItemDataRole.ForegroundRole, None)
        finally:
            self._updating = False

    # -- pre-run validation -------------------------------------------------------

    def _validate(self):
        """Recompute every row's predicted outcome and summarise any problems."""
        rows = range(self.table.rowCount())
        results = check_batch([(self._path(r), self._cell(r, "title")) for r in rows],
                              on_conflict=self.prefs["on_conflict"], output_dir=self._output_dir())
        problems = 0
        self._updating = True
        try:
            for row, (status, message) in zip(rows, results):
                item = self.table.item(row, COL["status"])
                item.setText(status)
                item.setToolTip(message)
                self.table.item(row, COL["title"]).setToolTip(
                    message if status in PROBLEM_STATUSES else "")
                problems += status in PROBLEM_STATUSES
        finally:
            self._updating = False
        for row in rows:
            self._color_status(row)
        self.issue_label.setText(
            f"⚠ {problems} naming problem{'s' if problems != 1 else ''}" if problems else "")
        self.issue_label.setToolTip("Hover over a red status for details." if problems else "")
        count = self.table.rowCount()
        self.file_count_label.setText(f"{count} file{'s' if count != 1 else ''}" if count else
                                      "none yet — add a folder or files, or drop PDFs here")
        return problems

    def _confirm_run_with_problems(self, problems):
        answer = QMessageBox.warning(
            self, "Naming problems",
            f"{problems} file{'s have' if problems != 1 else ' has'} a naming problem "
            "(missing title, duplicate name, or a file that already exists).\n\n"
            "Those files will be skipped or fail. Run anyway?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return answer == QMessageBox.StandardButton.Yes

    # -- table helpers ------------------------------------------------------------

    def _cell(self, row, col_name):
        item = self.table.item(row, COL[col_name])
        return item.text() if item else ""

    def _set_cell(self, row, col_name, value):
        self._updating = True
        try:
            self.table.item(row, COL[col_name]).setText(value)
        finally:
            self._updating = False
        if col_name == "status":
            self._color_status(row)

    def _path(self, row):
        return self.table.item(row, COL["file"]).data(PATH_ROLE)

    def _selected_row(self):
        rows = self.table.selectionModel().selectedRows()
        return rows[0].row() if rows else None

    # -- pattern builder / sample preview ---------------------------------------

    def _on_focus_changed(self, _old, new):
        if new in (self.title_pattern_edit, self.author_pattern_edit):
            self._active_pattern_edit = new

    def _insert_placeholder(self, placeholder):
        edit = self._active_pattern_edit
        edit.insert(placeholder)
        edit.setFocus()

    # -- presets --------------------------------------------------------------------

    def _current_patterns(self):
        return {"title": self.title_pattern_edit.text(),
                "author": self.author_pattern_edit.text(),
                "pad": self.pad_spin.value()}

    def _matching_preset(self):
        """Name of the preset identical to the current fields, or None."""
        current = self._current_patterns()
        return next((name for name in sorted(self.presets, key=str.lower)
                     if self.presets[name] == current), None)

    def _refresh_preset_combo(self, select=None):
        """Rebuild the preset list, selecting `select` (or whichever preset matches the fields)."""
        combo = self.preset_combo
        combo.blockSignals(True)
        combo.clear()
        combo.addItem("Choose a preset…" if self.presets else "No saved presets", None)
        for name in sorted(self.presets, key=str.lower):
            combo.addItem(name, name)
        combo.setCurrentIndex(max(0, combo.findData(select or self._matching_preset())))
        combo.blockSignals(False)
        self.delete_preset_button.setEnabled(combo.currentData() is not None)

    def _sync_preset_selection(self):
        """Keep the combo showing the preset the fields match, or the placeholder if none."""
        if not self._loading_preset and self.preset_combo.currentData() != self._matching_preset():
            self._refresh_preset_combo()

    def _on_preset_chosen(self, _index):
        name = self.preset_combo.currentData()
        self.delete_preset_button.setEnabled(name is not None)
        if name is None:
            return
        preset = self.presets[name]
        self._loading_preset = True
        try:
            self.title_pattern_edit.setText(preset["title"])
            self.author_pattern_edit.setText(preset["author"])
            self.pad_spin.setValue(preset["pad"])
        finally:
            self._loading_preset = False

    def save_preset(self):
        current = self._current_patterns()
        if not current["title"] and not current["author"]:
            QMessageBox.information(self, "Save Preset",
                                    "Enter a title or author pattern first, then save it as a preset.")
            return
        name, ok = QInputDialog.getText(self, "Save Preset", "Preset name:",
                                        text=self.preset_combo.currentData() or "")
        name = name.strip()
        if not ok or not name:
            return
        # Names are matched case-insensitively so "Chapters" and "chapters" can't both exist.
        existing = next((n for n in self.presets if n.lower() == name.lower()), None)
        if existing is not None and self.presets[existing] != current:
            answer = QMessageBox.question(
                self, "Replace Preset", f'A preset named "{existing}" already exists. Replace it?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            if answer != QMessageBox.StandardButton.Yes:
                return
        if existing is not None:
            del self.presets[existing]
        self.presets[name] = current
        self._save_presets()
        self._refresh_preset_combo(select=name)

    def delete_preset(self):
        name = self.preset_combo.currentData()
        if name is None:
            return
        answer = QMessageBox.question(
            self, "Delete Preset", f'Delete the preset "{name}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes:
            return
        del self.presets[name]
        self._save_presets()
        self._refresh_preset_combo()

    def _save_presets(self):
        self.settings.setValue("presets/json", json.dumps(self.presets))
        self.settings.sync()

    def _load_presets(self):
        try:
            raw = json.loads(self.settings.value("presets/json", "{}", type=str))
        except ValueError:
            raw = {}
        self.presets = {}
        for name, p in raw.items() if isinstance(raw, dict) else ():
            if isinstance(p, dict):
                self.presets[str(name)] = {"title": str(p.get("title", "")),
                                           "author": str(p.get("author", "")),
                                           "pad": max(0, min(10, int(p.get("pad", 0) or 0)))}
        self._refresh_preset_combo()

    def _update_sample(self):
        if self.table.rowCount():
            path = self._path(0)
            title, author = self._cell(0, "title"), self._cell(0, "author")
            source = path.name
        else:
            path, title, author = Path("example007.pdf"), "Sample Title", "Sample Author"
            source = "example007.pdf"

        def preview(pattern):
            if not pattern:
                return ""
            try:
                result = apply_pattern(pattern, path, existing_title=title, existing_author=author,
                                       pad=self.pad_spin.value())
            except ValueError as e:
                return f"({e})"
            return f"{source}  →  {result}"

        self.title_sample.setText(preview(self.title_pattern_edit.text()))
        self.author_sample.setText(preview(self.author_pattern_edit.text()))

    # -- reordering / removal -----------------------------------------------------

    def _move_row(self, offset):
        row = self._selected_row()
        if row is None:
            return
        target = row + offset
        if not 0 <= target < self.table.rowCount():
            return
        self._updating = True
        try:
            items = [self.table.takeItem(row, c) for c in range(len(COLUMNS))]
            self.table.removeRow(row)
            self.table.insertRow(target)
            for c, item in enumerate(items):
                self.table.setItem(target, c, item)
        finally:
            self._updating = False
        self.table.selectRow(target)
        self._update_sample()

    def move_row_up(self):
        self._move_row(-1)

    def move_row_down(self):
        self._move_row(1)

    def remove_selected_row(self):
        row = self._selected_row()
        if row is None:
            return
        self._added_paths.discard(str(self._path(row).resolve()))
        self.table.removeRow(row)
        self._validate()
        self._update_sample()

    # -- adding files -------------------------------------------------------------

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Add Folder", self.last_dir)
        if folder:
            self.last_dir = folder
            self._add_folder(Path(folder))

    def choose_files(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Add Files", self.last_dir, "PDF files (*.pdf)")
        if paths:
            self.last_dir = str(Path(paths[0]).parent)
        self._add_files(Path(p) for p in paths)

    def _add_folder(self, folder):
        files = folder.rglob("*") if self.prefs["include_subfolders"] else folder.iterdir()
        self._add_files(f for f in files if f.is_file() and f.suffix.lower() == ".pdf")

    def _sort_key(self, path):
        order = self.prefs["sort_order"]
        if order == "modified":
            try:
                return (0, path.stat().st_mtime)
            except OSError:
                return (1, 0)
        if order == "name":
            return str(path).lower()
        return natural_key(str(path))

    def _initial_title(self, path, meta_title):
        choice = self.prefs["initial_title"]
        if choice == "filename":
            return path.stem
        if choice == "blank":
            return ""
        return meta_title

    def _add_files(self, paths):
        paths = sorted(paths, key=self._sort_key)
        self._updating = True
        try:
            for path in paths:
                key = str(path.resolve())
                if key in self._added_paths:
                    continue
                self._added_paths.add(key)

                meta_title, meta_author = read_existing_metadata(path)
                row = self.table.rowCount()
                self.table.insertRow(row)
                values = (path.name, "", self._initial_title(path, meta_title), "", meta_author, "pending")
                for col_name, value in zip(COLUMNS, values):
                    item = QTableWidgetItem(value)
                    if col_name not in EDITABLE_COLUMNS:
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(row, COL[col_name], item)
                file_item = self.table.item(row, COL["file"])
                file_item.setData(PATH_ROLE, path)
                file_item.setToolTip(str(path))
        finally:
            self._updating = False
        self._validate()
        self._update_sample()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = []
        for url in event.mimeData().urls():
            path = Path(url.toLocalFile())
            if path.is_dir():
                self._add_folder(path)
            elif path.suffix.lower() == ".pdf":
                files.append(path)
        self._add_files(files)
        event.acceptProposedAction()

    def clear_file_list(self):
        """Remove all PDFs from the current batch list."""
        self.table.setRowCount(0)
        self._added_paths.clear()
        self._set_progress("Ready")
        self.progress_bar.setValue(0)
        self._validate()
        self._update_sample()

    def reset_app(self):
        """Clear all loaded files and reset naming pattern inputs."""
        self.clear_file_list()
        self.title_pattern_edit.clear()
        self.author_pattern_edit.clear()
        self.pad_spin.setValue(0)
        self.log_text.clear()

    # -- pattern application ------------------------------------------------------

    def apply_batch_title_pattern(self):
        self._apply_batch_pattern(self.title_pattern_edit.text(), "title_pattern", "title")

    def apply_batch_author_pattern(self):
        self._apply_batch_pattern(self.author_pattern_edit.text(), "author_pattern", "author")

    def _apply_batch_pattern(self, pattern, pattern_col, target_col):
        if not pattern:
            return
        for row in range(self.table.rowCount()):
            self._set_cell(row, pattern_col, pattern)
            self._recompute(row, pattern_col, target_col)
        self._validate()
        self._update_sample()

    def _recompute(self, row, pattern_col, target_col):
        """Re-apply the pattern in `pattern_col` for this row, writing the result into `target_col`."""
        pattern = self._cell(row, pattern_col)
        if not pattern:
            return
        path = self._path(row)
        try:
            result = apply_pattern(pattern, path, existing_title=self._cell(row, "title"),
                                   existing_author=self._cell(row, "author"),
                                   pad=self.pad_spin.value())
        except ValueError as e:
            self.log(f"{path.name}: {e}")
            return
        self._set_cell(row, target_col, result)

    def _on_pad_changed(self):
        """Re-apply every row's patterns so titles pick up the new padding."""
        for row in range(self.table.rowCount()):
            self._recompute(row, "title_pattern", "title")
            self._recompute(row, "author_pattern", "author")
        self._validate()
        self._update_sample()

    def _on_item_changed(self, item):
        """Handle a user edit of a table cell."""
        if self._updating:
            return
        col_name = COLUMNS[item.column()]
        if col_name == "title_pattern":
            self._recompute(item.row(), "title_pattern", "title")
        elif col_name == "author_pattern":
            self._recompute(item.row(), "author_pattern", "author")
        if col_name in ("title_pattern", "title"):
            self._validate()
        if item.row() == 0:
            self._update_sample()

    # -- running the batch --------------------------------------------------------

    def run_batch(self):
        total = self.table.rowCount()
        if total == 0 or not self.run_button.isEnabled():
            return
        problems = self._validate()
        if problems and not self._confirm_run_with_problems(problems):
            return

        output_dir = self._output_dir()
        on_conflict = self.prefs["on_conflict"]
        if output_dir is not None:
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                self.log(f"Can't create output folder {output_dir}: {e}")
                return
            self.log(f"Saving renamed copies to {output_dir}")

        self.run_button.setEnabled(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(0)
        counts = {"renamed": 0, "copied": 0, "skipped": 0, "failed": 0}

        try:
            for row in range(total):
                path = self._path(row)
                title = self._cell(row, "title")
                author = self._cell(row, "author") or None

                self._set_progress(f"Processing {row + 1} of {total}: {path.name}")
                QApplication.processEvents()

                if not title:
                    status = "failed"
                    self.log(f"{path.name}: no title set, skipping")
                else:
                    result = process_file(path, title, author,
                                          on_conflict=on_conflict, output_dir=output_dir)
                    status = result["status"]
                    self.log(f"{path.name}: {result['message']}")

                    if status == "renamed":
                        new_path = result["new_path"]
                        self._added_paths.discard(str(path.resolve()))
                        self._added_paths.add(str(new_path.resolve()))
                        file_item = self.table.item(row, COL["file"])
                        file_item.setData(PATH_ROLE, new_path)
                        file_item.setToolTip(str(new_path))
                        self._set_cell(row, "file", new_path.name)

                counts[status] += 1
                self._set_cell(row, "status", status)
                self.progress_bar.setValue(row + 1)
                QApplication.processEvents()
        finally:
            summary = ", ".join(f"{n} {s}" for s, n in counts.items() if n)
            self._set_progress(f"Done: {summary}" if summary else "Done")
            self.run_button.setEnabled(True)
            self.table.setEditTriggers(EDIT_TRIGGERS)
            self._update_sample()


def resource_path(name):
    """Path to a bundled file, both when run as a script and from a PyInstaller build."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / name


def main():
    if sys.platform == "win32":
        # Give the process its own taskbar identity; otherwise Windows groups it
        # under python.exe and shows Python's icon instead of ours.
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("PDFRenamer.App")

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))
    icon_file = resource_path("app.ico")
    if icon_file.exists():
        app.setWindowIcon(QIcon(str(icon_file)))  # applies to the main window and all dialogs
    window = App()
    window.showMaximized()  # always open maximized; the saved normal size applies when restored
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
