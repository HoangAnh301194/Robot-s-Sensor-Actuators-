import os
import shutil
import subprocess

src = "/home/hoang_anh/tb4_project_ab/images"
dst = "/home/hoang_anh/tb4_project_ab/src/Robots_Sensor_Actuators/Latex_report/images"

for root, dirs, files in os.walk(src):
    for f in files:
        if f.endswith('.png'):
            s = os.path.join(root, f)
            d = os.path.join(dst, os.path.relpath(s, src))
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy(s, d)

os.chdir("/home/hoang_anh/tb4_project_ab/src/Robots_Sensor_Actuators/Latex_report")
subprocess.run(["pdflatex", "-interaction=nonstopmode", "main.tex"])
subprocess.run(["pdflatex", "-interaction=nonstopmode", "main.tex"])
