import re

file_path = "/home/hoang_anh/tb4_project_ab/src/Robots_Sensor_Actuators/Latex_report/chapter2_theory.tex"

with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# Step 1: Replace \[ and \] with gather*
text = text.replace(r"\[", r"\begin{gather*}")
text = text.replace(r"\]", r"\end{gather*}")

# Step 2: Merge consecutive gather* blocks that are only separated by whitespace
pattern = re.compile(r"\\end\{gather\*\}\s*\\begin\{gather\*\}")
text = pattern.sub(r" \\\\[1.5ex]\n", text)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Merged equations successfully.")
