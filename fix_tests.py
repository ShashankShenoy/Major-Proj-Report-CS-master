import re

with open('Chapter7/07_SoftwareTesting.tex', 'r', encoding='utf-8') as f:
    content = f.read()

starts = [
    "The initial testing phase prioritized the evaluation",
    "Once baseline detection capabilities were established",
    "Following the latency bottlenecks identified during database-driven re-identification",
    "With detection and tracking stabilized, testing transitioned to mapping",
    "Recognizing the limitations of static imagery, the development pivoted",
    "The most computationally intensive component of the surveillance framework",
    "The final functional layer of the pipeline converts forecasted trajectories"
]

for start in starts:
    idx_start = content.find(start)
    if idx_start == -1: 
        print(f"Could not find start: {start}")
        continue
    
    idx_end = content.find(r"\end{table}", idx_start)
    if idx_end == -1: 
        print(f"Could not find end for: {start}")
        continue
    idx_end += len(r"\end{table}")
    
    block = content[idx_start:idx_end]
    
    # add \vspace{1em} between paragraph and table for better spacing
    block = block.replace(r"\begin{table}[H]", r"\vspace{1em}" + "\n" + r"\begin{table}[H]")
    
    wrapped_block = "\\noindent\\begin{minipage}{\\textwidth}\n" + block + "\n\\end{minipage}\n\\vspace{1em}"
    
    content = content[:idx_start] + wrapped_block + content[idx_end:]

with open('Chapter7/07_SoftwareTesting.tex', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done")
