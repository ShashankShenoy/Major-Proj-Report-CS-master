import re

with open('Chapter7/07_SoftwareTesting.tex', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = re.compile(r'\\noindent\\begin\{minipage\}\{\\textwidth\}\n.*?\n\\vspace\{1em\}\n\\begin\{table\}\[H\](.*?\n\\end\{table\})\n\\end\{minipage\}\n\\vspace\{1em\}', re.DOTALL)

new_content = pattern.sub(r'\\begin{table}[H]\1', content)

with open('Chapter7/07_SoftwareTesting.tex', 'w', encoding='utf-8') as f:
    f.write(new_content)
print("Done")
