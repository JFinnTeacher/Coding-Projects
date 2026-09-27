"""
Regenerate app.ico from icon.svg.

Renders the SVG at each standard Windows icon size with Qt and packs the
PNGs into a single multi-size .ico (PNG-compressed entries, Windows Vista+).
Qt's own ICO writer only stores one size, hence the manual packing.

Usage: python make_icon.py
"""

import struct
from pathlib import Path

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, Qt
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

HERE = Path(__file__).resolve().parent
SIZES = (16, 20, 24, 32, 40, 48, 64, 128, 256)


def render_png(renderer, size):
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    renderer.render(painter)
    painter.end()
    data = QByteArray()
    buffer = QBuffer(data)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(data)


def build_ico(pngs):
    """pngs: list of (size, png_bytes). Returns the .ico file contents."""
    header = struct.pack("<HHH", 0, 1, len(pngs))  # reserved, type=icon, count
    offset = len(header) + 16 * len(pngs)
    entries, blobs = b"", b""
    for size, png in pngs:
        dim = 0 if size >= 256 else size  # 0 means 256 in the ICO directory
        entries += struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32, len(png), offset)
        blobs += png
        offset += len(png)
    return header + entries + blobs


def main():
    app = QGuiApplication([])  # needed for font rendering of the SVG text
    renderer = QSvgRenderer(str(HERE / "icon.svg"))
    if not renderer.isValid():
        raise SystemExit("icon.svg could not be parsed")
    pngs = [(size, render_png(renderer, size)) for size in SIZES]
    (HERE / "app.ico").write_bytes(build_ico(pngs))
    (HERE / "icon.png").write_bytes(dict(pngs)[256])
    print(f"Wrote app.ico ({', '.join(map(str, SIZES))} px) and icon.png")
    del app


if __name__ == "__main__":
    main()
