"""Create a public source archive without credentials, captures, or build products."""
from pathlib import Path
import argparse
import zipfile
import yaml

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("output", type=Path)
args = parser.parse_args()
args.output.parent.mkdir(parents=True, exist_ok=True)
excluded_parts = {".git", ".esphome", ".venv", "__pycache__", "captures", "dist", "build"}
excluded_names = {"secrets.yaml", ".DS_Store", "settings-desktop.png", "settings-mobile.png", "learning-active.png"}
public_dirs = {".github", "assets", "docs", "examples", "firmware", "hardware", "licenses", "tests", "tools"}
public_extensions = {".md", ".txt", ".py", ".h", ".cpp", ".yaml", ".yml", ".js", ".css", ".html", ".svg", ".png", ".stl"}
secret_file = root / "firmware" / "secrets.yaml"
secrets = yaml.safe_load(secret_file.read_text()) if secret_file.exists() else {}
private_values = [str(v).encode() for v in (secrets or {}).values() if isinstance(v, str) and len(v) >= 6]
sources = []
for source in sorted(root.rglob("*")):
    relative = source.relative_to(root)
    if source.is_symlink() or not source.is_file() or excluded_parts.intersection(relative.parts):
        continue
    if source.name in excluded_names or source.resolve() == args.output.resolve():
        continue
    if len(relative.parts) > 1 and relative.parts[0] not in public_dirs:
        continue
    if source.suffix not in public_extensions and source.name not in {"LICENSE", ".gitignore"}:
        continue
    if any(value in source.read_bytes() for value in private_values):
        raise SystemExit(f"Private configuration value found in {relative}; publication refused")
    sources.append(source)
with zipfile.ZipFile(args.output, "w", zipfile.ZIP_DEFLATED) as archive:
    for source in sources:
        relative = source.relative_to(root)
        archive.write(source, Path("bzp-airbridge") / relative)
with zipfile.ZipFile(args.output) as archive:
    assert archive.testzip() is None
    assert not any(Path(n).name == "secrets.yaml" for n in archive.namelist())
    print(f"{len(archive.namelist())} files packaged; archive integrity passed")
