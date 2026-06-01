"""Ensure every reportfigblock has lead-in text before the inline figure."""
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
)


def is_stop_line(line: str) -> bool:
    s = line.strip()
    if not s or s.startswith("%"):
        return False
    return any(s.startswith(p) for p in STOP_PREFIXES)


def collect_lead_in(lines: list[str], block_idx: int) -> tuple[int, int]:
    j = block_idx - 1
    while j >= 0 and not lines[j].strip():
        j -= 1
    if j < 0:
        return block_idx, block_idx
    end = j
    start = j
    while start > 0:
        prev = start - 1
        if not lines[prev].strip():
            break
        if is_stop_line(lines[prev]):
            break
        start = prev
    return start, end + 1


def process_content(text: str) -> str:
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        if lines[i].strip() != "\\begin{reportfigblock}":
            out.append(lines[i])
            i += 1
            continue

        j = i + 1
        while j < n and lines[j].strip() != "\\end{reportfigblock}":
            j += 1

        block_body = lines[i + 1 : j]
        fig_idx = next(
            (k for k, ln in enumerate(block_body) if ln.strip().startswith("\\reportinline")),
            None,
        )

        lead_start, lead_end = collect_lead_in(lines, i)
        lead_lines = lines[lead_start:lead_end]

        # Drop duplicate lead-in already inside block
        if lead_lines and fig_idx is not None:
            lead_text = "\n".join(lead_lines).strip()
            before_fig = "\n".join(block_body[:fig_idx]).strip()
            if before_fig == lead_text:
                lead_lines = []

        # Move lead-in from document into block if figure is first
        if fig_idx == 0 and lead_lines:
            while len(out) > lead_start:
                out.pop()
            out.append("\\begin{reportfigblock}")
            out.extend(lead_lines)
            out.extend(block_body)
            out.append("\\end{reportfigblock}")
            i = j + 1
            continue

        # Block already has lead-in; remove external duplicate only
        if lead_lines and fig_idx and fig_idx > 0:
            before_fig = "\n".join(block_body[:fig_idx]).strip()
            if "\n".join(lead_lines).strip() == before_fig:
                while len(out) > lead_start:
                    out.pop()

        # Ensure minimum lead-in before figure inside block
        if fig_idx is not None and fig_idx == 0:
            # Add generic lead if still missing (should not happen often)
            out.append("\\begin{reportfigblock}")
            out.append(
                "The following figure summarizes the corresponding design element referenced in this section."
            )
            out.extend(block_body)
            out.append("\\end{reportfigblock}")
            i = j + 1
            continue

        out.extend(lines[i : j + 1])
        i = j + 1

    return "\n".join(out)


def main() -> None:
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        updated = process_content(text)
        path.write_text(updated, encoding="utf-8")
        missing = 0
        for m in re.finditer(r"\\begin\{reportfigblock\}(.*?)\\end\{reportfigblock\}", updated, re.DOTALL):
            body = m.group(1).lstrip()
            if body.startswith("\\reportinline"):
                missing += 1
        print(f"{path.name}: blocks without lead-in after fix: {missing}")


if __name__ == "__main__":
    main()
