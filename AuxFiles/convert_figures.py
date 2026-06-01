"""Move lead-in text into reportfigblock and use non-floating inline figures."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "Chapter4/04_hld.tex",
    ROOT / "Chapter5/05_detailed_design.tex",
    ROOT / "Chapter6/06_implementation.tex",
    ROOT / "Chapter8/08_ExpResults.tex",
]

STOP_PREFIXES = (
    "\\section{",
    "\\subsection{",
    "\\subsubsection{",
    "\\begin{",
    "\\end{",
    "\\FloatBarrier",
    "\\chapter{",
)

FIGURE_BLOCK = re.compile(
    r"\\begin\{reportfigwrap\}\s*"
    r"\\begin\{figure\}\[H\]\s*"
    r"\\centering\s*"
    r"\\report(?P<kind>diagram|screenshot)\{(?P<path>[^}]+)\}\s*"
    r"\\caption\{(?P<caption>.*?)\}\s*"
    r"\\label\{(?P<label>[^}]+)\}\s*"
    r"\\end\{figure\}\s*"
    r"(?P<after>.*?)"
    r"\\end\{reportfigwrap\}",
    re.DOTALL,
)


def is_stop_line(line: str) -> bool:
    s = line.strip()
    if not s or s.startswith("%"):
        return False
    return any(s.startswith(p) for p in STOP_PREFIXES)


def collect_lead_in(lines: list[str], wrap_idx: int) -> tuple[int, int]:
    j = wrap_idx - 1
    while j >= 0 and not lines[j].strip():
        j -= 1
    if j < 0:
        return wrap_idx, wrap_idx
    end = j
    start = j
    while start >= 0:
        if not lines[start].strip():
            break
        if is_stop_line(lines[start]):
            start += 1
            break
        if start < end and lines[start].strip().startswith("\\"):
            break
        start -= 1
    start += 1
    if end > start:
        last = "\n".join(lines[start : end + 1])
        if len(last) > 900 and not re.search(r"\\ref\{", last):
            start = end
    return start, end + 1


def inline_figure(kind: str, path: str, caption: str, label: str) -> str:
    cmd = "reportinlinediagram" if kind == "diagram" else "reportinlinescreenshot"
    return f"\\{cmd}{{{path}}}{{{caption.strip()}}}{{{label}}}"


def process_content(text: str) -> str:
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        if lines[i].strip() != "\\begin{reportfigwrap}":
            out.append(lines[i])
            i += 1
            continue

        lead_start, lead_end = collect_lead_in(lines, i)
        while len(out) > lead_start:
            out.pop()

        j = i
        while j < n and lines[j].strip() != "\\end{reportfigwrap}":
            j += 1
        block = "\n".join(lines[i : j + 1])
        m = FIGURE_BLOCK.search(block)
        if not m:
            out.extend(lines[lead_start : j + 1])
            i = j + 1
            continue

        out.append("\\begin{reportfigblock}")
        if lead_end > lead_start:
            out.extend(lines[lead_start:lead_end])
        out.append(
            inline_figure(
                m.group("kind"), m.group("path"), m.group("caption"), m.group("label")
            )
        )
        after = m.group("after").strip()
        if after:
            out.extend(after.split("\n"))
        out.append("\\end{reportfigblock}")
        i = j + 1

    return "\n".join(out)


def main() -> None:
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        count = text.count("\\begin{reportfigwrap}")
        updated = process_content(text)
        path.write_text(updated, encoding="utf-8")
        print(
            f"{path.name}: {count} blocks -> "
            f"{updated.count('reportinline')} inline, "
            f"{updated.count('begin{reportfigblock}')} blocks"
        )


if __name__ == "__main__":
    main()
