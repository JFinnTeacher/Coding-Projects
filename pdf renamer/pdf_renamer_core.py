"""
Core logic for PDF Renamer: batch-renames PDFs and sets their /Title (and
/Author) metadata using pypdf. No GUI dependencies, so it can be imported and
used headless (and is what tests/test_core.py exercises).

The GUI lives in pdf-renamer-v2.py.
"""

import os
import re
from pathlib import Path

from pypdf import PdfReader, PdfWriter

INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*]')


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
        # append() copies pages only; carry the document info over too, so fields we
        # don't set (Subject, Keywords, Creator, dates, and Author when blank) survive.
        if reader.metadata:
            writer.add_metadata(reader.metadata)

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
