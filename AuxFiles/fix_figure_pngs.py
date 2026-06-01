"""Normalize PNG DPI and pixel size for LaTeX (Chapters 3--5 figures)."""
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = None  # allow oversized exports before rescale

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "Chapter3/Figures/system_architecture.png",
    ROOT / "Chapter3/Figures/deployment_architecture.png",
    ROOT / "Chapter3/Figures/fig3_use_case_diagram.png",
    *sorted((ROOT / "Chapter4/Figures").glob("*.png")),
    *sorted((ROOT / "Chapter5/Figures").glob("*.png")),
]
MAX_DIM = 2400
DPI = 150


def fix_png(path: Path) -> str:
    if not path.exists():
        return f"missing: {path}"
    im = Image.open(path)
    w, h = im.size
    if max(w, h) > MAX_DIM:
        scale = MAX_DIM / max(w, h)
        w, h = int(w * scale), int(h * scale)
        im = im.resize((w, h), Image.Resampling.LANCZOS)
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    im.save(path, format="PNG", dpi=(DPI, DPI), optimize=True)
    return f"{path.name}: {w}x{h} @ {DPI}dpi"


def main() -> None:
    for path in TARGETS:
        print(fix_png(path))


if __name__ == "__main__":
    main()
