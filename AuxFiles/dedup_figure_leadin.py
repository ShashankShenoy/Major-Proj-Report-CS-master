"""Remove duplicate lead-in paragraphs immediately before reportfigblock."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "Chapter4/04_hld.tex",
    ROOT / "Chapter5/05_detailed_design.tex",
    ROOT / "Chapter6/06_implementation.tex",
    ROOT / "Chapter8/08_ExpResults.tex",
]


def process(text: str) -> str:
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        if lines[i].strip() != "\\begin{reportfigblock}":
            out.append(lines[i])
            i += 1
            continue
        j = i + 1
        while j < len(lines) and lines[j].strip() != "\\end{reportfigblock}":
            j += 1
        body = [ln for ln in lines[i + 1 : j] if ln.strip()]
        if body and not body[0].strip().startswith("\\reportinline"):
            first = body[0].strip()
            k = len(out) - 1
            while k >= 0 and not out[k].strip():
                k -= 1
            if k >= 0 and out[k].strip() == first:
                out.pop(k)
                while out and not out[-1].strip():
                    out.pop()
        out.extend(lines[i : j + 1])
        i = j + 1
    return "\n".join(out)


for path in FILES:
    updated = process(path.read_text(encoding="utf-8"))
    path.write_text(updated, encoding="utf-8")
    print(f"deduped {path.name}")
