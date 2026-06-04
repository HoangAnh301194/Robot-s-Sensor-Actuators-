import glob
import re

for filename in glob.glob("*.tex"):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Remove blank lines before \begin{gather*} and \[
    # We look for a newline, then any amount of whitespace (including newlines), then the math environment
    # Wait, \n\s*\n matches multiple empty lines.
    content = re.sub(r'\n[ \t\r]*\n[ \t\r]*\\begin\{gather\*\}', r'\n\\begin{gather*}', content)
    content = re.sub(r'\\end\{gather\*\}\n[ \t\r]*\n', r'\\end{gather*}\n', content)
    
    content = re.sub(r'\n[ \t\r]*\n[ \t\r]*\\\[', r'\n\\[', content)
    content = re.sub(r'\\\]\n[ \t\r]*\n', r'\\]\n', content)
    
    # Also for align* and equation*
    content = re.sub(r'\n[ \t\r]*\n[ \t\r]*\\begin\{align\*\}', r'\n\\begin{align*}', content)
    content = re.sub(r'\\end\{align\*\}\n[ \t\r]*\n', r'\\end{align*}\n', content)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

print("Fixed math spacing.")
