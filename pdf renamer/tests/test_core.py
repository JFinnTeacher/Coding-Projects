"""Tests for pdf_renamer_core: pattern handling, pre-run checks and file processing."""

import sys
from pathlib import Path

import pytest
from pypdf import PdfReader, PdfWriter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pdf_renamer_core import (  # noqa: E402
    apply_pattern, check_batch, extract_number, natural_key, process_file,
    read_existing_metadata, sanitize_filename, target_path, unique_path,
)


def make_pdf(path, title="Original", author=None):
    writer = PdfWriter()
    writer.add_blank_page(100, 100)
    metadata = {"/Title": title}
    if author:
        metadata["/Author"] = author
    writer.add_metadata(metadata)
    with open(path, "wb") as f:
        writer.write(f)
    return path


def meta(path):
    m = PdfReader(str(path)).metadata
    return m.get("/Title"), m.get("/Author")


def names(folder):
    return sorted(p.name for p in folder.iterdir())


# -- small helpers ------------------------------------------------------------------

@pytest.mark.parametrize("text, expected", [
    ("scan7", 7), ("scan007", 7), ("2024_scan_07", 2024), ("no digits", None),
])
def test_extract_number_takes_first_run_of_digits(text, expected):
    assert extract_number(text) == expected


def test_sanitize_filename_strips_windows_invalid_characters():
    assert sanitize_filename(' a<b>c:d"e/f\\g|h?i*j ') == "abcdefghij"


def test_natural_key_orders_numbers_numerically():
    files = ["scan10.pdf", "scan2.pdf", "Scan1.pdf"]
    assert sorted(files, key=natural_key) == ["Scan1.pdf", "scan2.pdf", "scan10.pdf"]


def test_target_path_in_place_and_output_dir(tmp_path):
    src = tmp_path / "scan1.pdf"
    assert target_path(src, "Doc: 1") == tmp_path / "Doc 1.pdf"
    assert target_path(src, "Doc", output_dir=tmp_path / "out") == tmp_path / "out" / "Doc.pdf"
    assert target_path(src, "") is None
    assert target_path(src, "???") is None


def test_unique_path_skips_existing_and_claimed_names(tmp_path):
    (tmp_path / "Doc.pdf").touch()
    assert unique_path(tmp_path / "Doc.pdf") == tmp_path / "Doc (2).pdf"
    claimed = {str(tmp_path / "Doc (2).pdf").lower(), str(tmp_path / "Doc (2).pdf")}
    assert unique_path(tmp_path / "Doc.pdf", claimed) == tmp_path / "Doc (3).pdf"
    assert unique_path(tmp_path / "Free.pdf") == tmp_path / "Free.pdf"


# -- apply_pattern ------------------------------------------------------------------

def test_apply_pattern_substitutes_placeholders():
    result = apply_pattern("{n} - {title} by {author}", Path("scan7.pdf"),
                           existing_title="Intro", existing_author="Jim")
    assert result == "7 - Intro by Jim"


def test_apply_pattern_padding():
    assert apply_pattern("{n}", Path("x7.pdf"), pad=3) == "007"
    assert apply_pattern("{n}", Path("x1234.pdf"), pad=3) == "1234"  # never truncates
    assert apply_pattern("{n:02d}", Path("x7.pdf"), pad=5) == "07"   # explicit spec wins
    assert apply_pattern("{n}", Path("x7.pdf"), pad=0) == "7"


def test_apply_pattern_without_a_number_gives_empty_n():
    assert apply_pattern("Doc {n}", Path("readme.pdf"), pad=3) == "Doc "


@pytest.mark.parametrize("pattern", ["{unknown}", "{n:zz}", "{0}", "{title"])
def test_apply_pattern_rejects_invalid_patterns(pattern):
    with pytest.raises(ValueError):
        apply_pattern(pattern, Path("scan7.pdf"), existing_title="T")


# -- check_batch --------------------------------------------------------------------

def test_check_batch_statuses_in_skip_mode(tmp_path):
    a, b, c, d = (make_pdf(tmp_path / f"{n}.pdf") for n in ("scan1", "scan2", "copy2", "Doc 9"))
    make_pdf(tmp_path / "Taken.pdf")
    results = check_batch([(a, "Doc 1"), (b, "Doc 2"), (c, "doc 2"), (d, "Doc 9"),
                           (a, "Taken"), (a, "")])
    assert [s for s, _ in results] == ["ready", "duplicate", "duplicate", "unchanged",
                                       "exists", "no title"]
    assert "row 3" in results[1][1]  # duplicate message names the clashing row


def test_check_batch_suffix_mode_hands_out_numbered_names(tmp_path):
    a, b = make_pdf(tmp_path / "scan1.pdf"), make_pdf(tmp_path / "scan2.pdf")
    make_pdf(tmp_path / "Doc.pdf")
    results = check_batch([(a, "Doc"), (b, "Doc")], on_conflict="suffix")
    assert [s for s, _ in results] == ["suffix", "suffix"]
    assert "Doc (2).pdf" in results[0][1] and "Doc (3).pdf" in results[1][1]


def test_check_batch_overwrite_mode(tmp_path):
    a, b = make_pdf(tmp_path / "scan1.pdf"), make_pdf(tmp_path / "scan2.pdf")
    make_pdf(tmp_path / "Old.pdf")
    results = check_batch([(a, "Old"), (b, "scan1")], on_conflict="overwrite")
    assert results[0][0] == "overwrite"
    # Row 2's target is row 1's source file: overwriting it would destroy that file.
    assert results[1][0] == "exists" and "row 1" in results[1][1]


def test_check_batch_output_dir_targets_the_output_folder(tmp_path):
    src = make_pdf(tmp_path / "Doc.pdf")
    out = tmp_path / "out"
    assert check_batch([(src, "Doc")])[0][0] == "unchanged"
    assert check_batch([(src, "Doc")], output_dir=out)[0][0] == "ready"


# -- process_file -------------------------------------------------------------------

def test_process_file_renames_in_place_and_sets_metadata(tmp_path):
    src = make_pdf(tmp_path / "scan1.pdf")
    result = process_file(src, "Chapter: 1", author="Jim")
    assert result["status"] == "renamed"
    assert names(tmp_path) == ["Chapter 1.pdf"]  # ':' removed from the filename...
    assert meta(tmp_path / "Chapter 1.pdf") == ("Chapter: 1", "Jim")  # ...but kept in metadata


def test_process_file_without_author_keeps_existing_author(tmp_path):
    src = make_pdf(tmp_path / "scan1.pdf", author="Original Author")
    process_file(src, "New")
    assert meta(tmp_path / "New.pdf") == ("New", "Original Author")


def test_process_file_preserves_other_metadata(tmp_path):
    src = tmp_path / "scan1.pdf"
    writer = PdfWriter()
    writer.add_blank_page(100, 100)
    writer.add_metadata({"/Title": "Old", "/Subject": "Taxes", "/Keywords": "2024, receipts"})
    with open(src, "wb") as f:
        writer.write(f)
    process_file(src, "New", author="Jim")
    m = PdfReader(str(tmp_path / "New.pdf")).metadata
    assert (m["/Title"], m["/Author"], m["/Subject"], m["/Keywords"]) == \
        ("New", "Jim", "Taxes", "2024, receipts")


def test_process_file_skips_when_already_named(tmp_path):
    src = make_pdf(tmp_path / "Doc.pdf")
    assert process_file(src, "Doc")["status"] == "skipped"
    assert names(tmp_path) == ["Doc.pdf"]


def test_process_file_skip_mode_leaves_both_files_untouched(tmp_path):
    src = make_pdf(tmp_path / "scan1.pdf", title="source")
    make_pdf(tmp_path / "Doc.pdf", title="existing")
    result = process_file(src, "Doc")
    assert result["status"] == "skipped"
    assert names(tmp_path) == ["Doc.pdf", "scan1.pdf"]
    assert meta(tmp_path / "Doc.pdf")[0] == "existing"


def test_process_file_suffix_mode(tmp_path):
    src = make_pdf(tmp_path / "scan1.pdf")
    make_pdf(tmp_path / "Doc.pdf", title="existing")
    result = process_file(src, "Doc", on_conflict="suffix")
    assert result["status"] == "renamed" and result["new_path"].name == "Doc (2).pdf"
    assert names(tmp_path) == ["Doc (2).pdf", "Doc.pdf"]
    assert meta(tmp_path / "Doc.pdf")[0] == "existing"


def test_process_file_overwrite_mode_replaces_existing(tmp_path):
    src = make_pdf(tmp_path / "scan1.pdf")
    make_pdf(tmp_path / "Doc.pdf", title="existing")
    result = process_file(src, "Doc", on_conflict="overwrite")
    assert result["status"] == "renamed" and "replaced" in result["message"]
    assert names(tmp_path) == ["Doc.pdf"]
    assert meta(tmp_path / "Doc.pdf")[0] == "Doc"


def test_process_file_output_dir_copies_and_keeps_original(tmp_path):
    src = make_pdf(tmp_path / "scan1.pdf", title="source")
    out = tmp_path / "out"
    out.mkdir()
    result = process_file(src, "Doc", output_dir=out)
    assert result["status"] == "copied"
    assert (tmp_path / "scan1.pdf").exists() and meta(tmp_path / "scan1.pdf")[0] == "source"
    assert names(out) == ["Doc.pdf"] and meta(out / "Doc.pdf")[0] == "Doc"


def test_process_file_empty_title_fails_without_touching_file(tmp_path):
    src = make_pdf(tmp_path / "scan1.pdf")
    assert process_file(src, "  ")["status"] == "failed"
    assert names(tmp_path) == ["scan1.pdf"]


def test_process_file_unreadable_pdf_fails_cleanly(tmp_path):
    bad = tmp_path / "broken.pdf"
    bad.write_bytes(b"this is not a pdf")
    result = process_file(bad, "Doc")
    assert result["status"] == "failed"
    # Original kept, no half-written target, no leftover temp file.
    assert names(tmp_path) == ["broken.pdf"]


def test_read_existing_metadata(tmp_path):
    assert read_existing_metadata(make_pdf(tmp_path / "a.pdf", "T", "A")) == ("T", "A")
    bad = tmp_path / "bad.pdf"
    bad.write_bytes(b"junk")
    assert read_existing_metadata(bad) == ("", "")
