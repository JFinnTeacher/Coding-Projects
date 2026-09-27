"""Smoke test: build the main window headlessly and run a small batch end to end."""

import importlib.util
import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")  # no window on screen

from PySide6.QtCore import QSettings  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from test_core import make_pdf, meta, names  # noqa: E402

APP_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def gui():
    """The pdf-renamer-v2 module (hyphenated filename, so loaded by path)."""
    spec = importlib.util.spec_from_file_location("pdf_renamer_gui", APP_DIR / "pdf-renamer-v2.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def window(gui, tmp_path):
    app = QApplication.instance() or QApplication([])
    # Keep the user's real %APPDATA% settings out of it.
    QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, str(tmp_path / "settings"))
    w = gui.App()
    w._confirm_run_with_problems = lambda problems: True  # no modal dialog in tests
    yield w
    w.close()
    app.processEvents()


def cells(w, column):
    return [w._cell(r, column) for r in range(w.table.rowCount())]


def test_batch_end_to_end(window, tmp_path):
    folder = tmp_path / "pdfs"
    folder.mkdir()
    for n in ("scan10", "scan2", "copy2"):
        make_pdf(folder / f"{n}.pdf")

    window._add_folder(folder)
    assert cells(window, "file") == ["copy2.pdf", "scan2.pdf", "scan10.pdf"]  # natural sort
    assert window.file_count_label.text() == "3 files"

    window.title_pattern_edit.setText("Doc {n}")
    window.pad_spin.setValue(2)
    window.apply_batch_title_pattern()
    assert cells(window, "title") == ["Doc 02", "Doc 02", "Doc 10"]
    assert cells(window, "status") == ["duplicate", "duplicate", "ready"]

    window.prefs["on_conflict"] = "suffix"
    window._validate()
    assert cells(window, "status") == ["ready", "suffix", "ready"]

    window.run_batch()
    assert cells(window, "status") == ["renamed", "renamed", "renamed"]
    assert names(folder) == ["Doc 02 (2).pdf", "Doc 02.pdf", "Doc 10.pdf"]
    assert meta(folder / "Doc 10.pdf")[0] == "Doc 10"


def test_presets_round_trip(window, gui, monkeypatch):
    window.title_pattern_edit.setText("Chapter {n}")
    window.pad_spin.setValue(3)
    monkeypatch.setattr(gui.QInputDialog, "getText", staticmethod(lambda *a, **k: ("Chapters", True)))
    window.save_preset()
    window.title_pattern_edit.clear()
    window.pad_spin.setValue(0)

    window.preset_combo.setCurrentIndex(window.preset_combo.findData("Chapters"))
    window._on_preset_chosen(0)
    assert window._current_patterns() == {"title": "Chapter {n}", "author": "", "pad": 3}
