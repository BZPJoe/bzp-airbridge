"""Render the original SVG brand/diagram assets to portable PNG files."""
from pathlib import Path
import resvg_py

root = Path(__file__).resolve().parents[1]
for name in ("icon", "wordmark", "wiring", "cover"):
    source = root / "assets" / (name + ".svg")
    width = 512 if name == "icon" else None
    data = resvg_py.svg_to_bytes(svg_path=str(source), width=width)
    source.with_suffix(".png").write_bytes(data)
    print(source.with_suffix(".png").name)
