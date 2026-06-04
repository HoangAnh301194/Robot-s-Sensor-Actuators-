import re

file_path = "/home/hoang_anh/tb4_project_ab/src/Robots_Sensor_Actuators/Latex_report/chapter2_theory.tex"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

replacements = {
    "fig:closed-loop": r"""\begin{figure}[H]
    \centering
    \resizebox{0.95\textwidth}{!}{
    \begin{tikzpicture}[
        font=\small,
        node distance=1.2cm and 1.0cm,
        block/.style={
            rectangle, rounded corners=3pt, draw=black, thick,
            align=center, minimum height=1.0cm, minimum width=2.4cm,
            text width=2.4cm
        },
        arrow/.style={-{Stealth[length=2.5mm]}, thick}
    ]
    \node[block, fill=blue!10] (env) {Môi trường};
    \node[block, fill=green!12, right=of env] (sensor) {Cảm biến\\LiDAR, Camera\\Encoder};
    \node[block, fill=orange!12, right=of sensor] (process) {Xử lý\\SLAM, YOLO\\Localization};
    \node[block, fill=yellow!15, right=of process] (control) {Điều khiển\\Nav2\\Mission Manager};
    \node[block, fill=red!10, below=1.0cm of control] (actuator) {Cơ cấu chấp hành\\Truyền động vi sai};

    \draw[arrow] (env) -- (sensor);
    \draw[arrow] (sensor) -- (process);
    \draw[arrow] (process) -- (control);
    \draw[arrow] (control) -- (actuator);
    \draw[arrow] (actuator.west) -- ++(-7.5,0) |- (env.south);
    \end{tikzpicture}
    }
    \caption{Sơ đồ vòng kín cảm biến -- xử lý -- điều khiển -- chấp hành}
    \label{fig:closed-loop}
\end{figure}""",
    
    "fig:lidar-principle": r"""\begin{figure}[H]
\centering
\begin{tikzpicture}[>=Latex, thick]
\node[circle, draw, minimum size=1.5cm, fill=black!10] (robot) {LiDAR};
\foreach \angle in {0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330} {
    \draw[->, red!70, dashed] (robot.center) -- (\angle:2.5cm);
}
\draw[blue, very thick] (-10:2.8cm) arc (-10:130:2.8cm) node[midway, right] {Biên dạng vật cản};
\draw[blue, very thick] (170:2.8cm) arc (170:280:2.8cm);
\end{tikzpicture}
\caption{Nguyên lý LiDAR 2D quét laser quanh robot và tạo tập điểm khoảng cách}
\label{fig:lidar-principle}
\end{figure}""",

    "fig:rgbd-flow": r"""\begin{figure}[H]
\centering
\begin{tikzpicture}[node distance=1.5cm and 2cm, every node/.style={draw, rounded corners, align=center, fill=blue!5}, >=Latex]
\node (cam) [minimum height=2cm] {Camera OAK-D};
\node (rgb) [right=of cam, yshift=1cm] {Ảnh RGB\\\texttt{image\_raw}};
\node (depth) [right=of cam, yshift=0cm] {Ảnh Depth\\\texttt{depth}};
\node (info) [right=of cam, yshift=-1cm] {Thông số nội tại\\\texttt{camera\_info}};
\draw[->] (cam.east) -- (rgb.west);
\draw[->] (cam.east) -- (depth.west);
\draw[->] (cam.east) -- (info.west);
\end{tikzpicture}
\caption{Camera RGB-D OAK-D gồm luồng ảnh RGB, ảnh depth và thông số nội tại camera}
\label{fig:rgbd-flow}
\end{figure}""",

    "fig:encoder-odometry": r"""\begin{figure}[H]
\centering
\begin{tikzpicture}[node distance=1.5cm, every node/.style={draw, rounded corners, align=center, fill=green!5}, >=Latex]
\node (enc) {Encoder trái/phải\\(Xung/Góc quay)};
\node (odom) [right=of enc] {Mô hình động học\\(Kinematics)};
\node (pose) [right=of odom] {Odometry\\($x, y, \theta, v, \omega$)};
\draw[->] (enc) -- (odom);
\draw[->] (odom) -- (pose);
\end{tikzpicture}
\caption{Encoder đo góc quay hai bánh và suy ra chuyển động của robot vi sai}
\label{fig:encoder-odometry}
\end{figure}""",

    "fig:tf-tree": r"""\begin{figure}[H]
\centering
\begin{tikzpicture}[node distance=1.5cm and 2cm, every node/.style={draw, rounded corners, font=\ttfamily, fill=white}, >=Latex]
\node (map) {map};
\node (odom) [right=of map] {odom};
\node (base) [right=of odom] {base\_link};
\node (lidar) [above right=0.3cm and 1.2cm of base] {rplidar\_link};
\node (oakd) [below right=0.3cm and 1.2cm of base] {oakd\_link};
\draw[->, thick] (map) -- node[above, font=\small\rmfamily, draw=none] {SLAM} (odom);
\draw[->, thick] (odom) -- node[above, font=\small\rmfamily, draw=none] {Odometry} (base);
\draw[->, thick] (base) -| node[above, font=\small\rmfamily, pos=0.25, draw=none] {URDF (Tĩnh)} (lidar);
\draw[->, thick] (base) -| (oakd);
\end{tikzpicture}
\caption{Cây TF của hệ thống TurtleBot4}
\label{fig:tf-tree}
\end{figure}""",

    "fig:slam-flow": r"""\begin{figure}[H]
\centering
\begin{tikzpicture}[node distance=1.5cm, every node/.style={draw, rounded corners, fill=orange!5}, >=Latex]
\node (scan) {LiDAR /scan};
\node (odom) [below=0.5cm of scan] {Odometry /odom};
\node (tf) [below=0.5cm of odom] {TF /tf};
\node (slam) [right=1.5cm of odom, minimum height=3cm, fill=orange!20, align=center] {SLAM\\Toolbox};
\node (map) [right=1.5cm of slam, yshift=0.8cm] {Bản đồ (map)};
\node (pose) [right=1.5cm of slam, yshift=-0.8cm] {TF map $\rightarrow$ odom};
\draw[->] (scan) -- (slam.160);
\draw[->] (odom) -- (slam.180);
\draw[->] (tf) -- (slam.200);
\draw[->] (slam.20) -- (map);
\draw[->] (slam.340) -- (pose);
\end{tikzpicture}
\caption{SLAM sử dụng LiDAR, odometry và TF để tạo bản đồ và pose robot}
\label{fig:slam-flow}
\end{figure}""",

    "fig:nav2-flow": r"""\begin{figure}[H]
\centering
\begin{tikzpicture}[node distance=1.0cm and 1.2cm, every node/.style={draw, rounded corners, align=center, fill=cyan!5}, >=Latex]
\node (goal) {Goal\\(NavigateToPose)};
\node (global) [right=of goal] {Global Planner\\(Đường đi toàn cục)};
\node (local) [right=of global] {Local Controller\\(Tránh vật cản)};
\node (cmd) [right=of local] {Lệnh vận tốc\\/cmd\_vel};
\draw[->] (goal) -- (global);
\draw[->] (global) -- (local);
\draw[->] (local) -- (cmd);
\end{tikzpicture}
\caption{Luồng điều hướng Nav2 từ goal đến global planner, local controller và /cmd\_vel}
\label{fig:nav2-flow}
\end{figure}""",

    "fig:yolo-flow": r"""\begin{figure}[H]
\centering
\begin{tikzpicture}[node distance=1.5cm, every node/.style={draw, rounded corners, align=center, fill=yellow!10}, >=Latex]
\node (img) {Ảnh RGB};
\node (yolo) [right=of img] {Mô hình\\YOLOv8n};
\node (det) [right=of yolo, align=left] {Bounding box\\Class ID\\Confidence};
\draw[->] (img) -- (yolo);
\draw[->] (yolo) -- (det);
\end{tikzpicture}
\caption{YOLOv8 nhận ảnh RGB và xuất bounding box, class id, confidence}
\label{fig:yolo-flow}
\end{figure}""",

    "fig:localization-flow": r"""\begin{figure}[H]
\centering
\begin{tikzpicture}[node distance=1.5cm, every node/.style={draw, rounded corners, fill=purple!5}, >=Latex]
\node (bbox) {Bounding Box};
\node (depth) [below=0.5cm of bbox] {Ảnh Depth};
\node (info) [below=0.5cm of depth] {CameraInfo};
\node (loc) [right=1.5cm of depth, minimum height=3cm, fill=purple!20, align=center] {Object\\Localization};
\node (pose) [right=1.5cm of loc] {Target Pose 3D};
\draw[->] (bbox) -- (loc.160);
\draw[->] (depth) -- (loc.180);
\draw[->] (info) -- (loc.200);
\draw[->] (loc) -- (pose);
\end{tikzpicture}
\caption{Quy trình bbox, depth và CameraInfo tạo target pose 3D}
\label{fig:localization-flow}
\end{figure}""",

    "fig:differential-drive-model": r"""\begin{figure}[H]
\centering
\begin{tikzpicture}[>=Latex, thick]
\draw[fill=black!5] (0,0) circle (1.5cm);
\draw[fill=black!50] (-0.4, 1.3) rectangle (0.4, 1.7) node[above=0.1cm, black] {Bánh trái ($v_l, \omega_l$)};
\draw[fill=black!50] (-0.4, -1.7) rectangle (0.4, -1.3) node[below=0.1cm, black] {Bánh phải ($v_r, \omega_r$)};
\draw[<->, red] (0, 1.3) -- (0, -1.3) node[midway, right] {$L$};
\draw[->, blue, ultra thick] (0,0) -- (2.0,0) node[right] {$v$};
\draw[->, blue, ultra thick] (0.8,0) arc (0:60:0.8cm) node[right] {$\omega$};
\draw[->] (0, 1.5) -- (-1.2, 1.5) node[left] {$r$ (bán kính)};
\end{tikzpicture}
\caption{Mô hình robot vi sai với hai bánh chủ động, bán kính bánh $r$ và khoảng cách bánh $L$}
\label{fig:differential-drive-model}
\end{figure}""",

    "fig:mission-manager-state": r"""\begin{figure}[H]
\centering
\begin{tikzpicture}[node distance=4cm, every node/.style={draw, rounded corners, circle, minimum size=2.5cm, align=center, fill=teal!10}, >=Latex]
\node (patrol) {Patrol\\(Tuần tra)};
\node (approach) [right=of patrol] {Approach\\(Tiếp cận)};
\draw[->, thick, bend left=20] (patrol) to node[above, draw=none, fill=none] {Phát hiện mục tiêu} (approach);
\draw[->, thick, bend left=20] (approach) to node[below, draw=none, fill=none] {Tiếp cận xong / Mất dấu} (patrol);
\end{tikzpicture}
\caption{Mission Manager chuyển từ trạng thái tuần tra sang tiếp cận mục tiêu rồi quay lại tuần tra}
\label{fig:mission-manager-state}
\end{figure}""",

    "fig:overall-dataflow": r"""\begin{figure}[H]
\centering
\resizebox{\textwidth}{!}{
\begin{tikzpicture}[node distance=1.2cm and 1.5cm, every node/.style={draw, rounded corners, align=center, fill=gray!10}, >=Latex]
\node (cam) {Camera};
\node (yolo) [right=of cam] {YOLOv8};
\node (loc) [right=of yolo] {Object\\Localization};
\node (mission) [right=of loc] {Mission\\Manager};
\node (nav) [right=of mission] {Nav2};
\node (act) [right=of nav] {Differential\\Drive};

\node (lidar) [below=1.5cm of yolo] {LiDAR};
\node (slam) [right=of lidar] {SLAM};

\draw[->, thick] (cam) -- node[above, draw=none, fill=none, font=\footnotesize] {RGB} (yolo);
\draw[->, thick] (yolo) -- node[above, draw=none, fill=none, font=\footnotesize] {BBox} (loc);
\draw[->, thick] (cam.south) |- node[above, draw=none, fill=none, font=\footnotesize, pos=0.75] {Depth} (loc.west);
\draw[->, thick] (loc) -- node[above, draw=none, fill=none, font=\footnotesize] {Pose 3D} (mission);
\draw[->, thick] (mission) -- node[above, draw=none, fill=none, font=\footnotesize] {Goal} (nav);
\draw[->, thick] (nav) -- node[above, draw=none, fill=none, font=\footnotesize] {/cmd\_vel} (act);

\draw[->, thick] (lidar) -- node[above, draw=none, fill=none, font=\footnotesize] {/scan} (slam);
\draw[->, thick] (slam) -| node[near end, right, draw=none, fill=none, font=\footnotesize] {Map, TF} (nav);
\end{tikzpicture}
}
\caption{Luồng dữ liệu tổng hợp từ camera, LiDAR, SLAM, YOLOv8, Mission Manager đến Nav2 và cơ cấu chấp hành}
\label{fig:overall-dataflow}
\end{figure}"""
}

# The regex searches for \placeholderfigure{...}{...}{key}
pattern = re.compile(r'\\placeholderfigure\{[^}]*\}\{[^}]*\}\{([^}]+)\}')

def replacer(match):
    key = match.group(1)
    if key in replacements:
        return replacements[key]
    return match.group(0)

new_content = pattern.sub(replacer, content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)
