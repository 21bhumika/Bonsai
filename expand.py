import random
import math
import re
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev
from util import import_tree_from_json

# === 给 trunk 和 branch 路径添加宽度 ===
def assign_path_widths(trunks, branches, trunk_main_width=50, trunk_min_width=7, branch_start=10, branch_end=0.1):
    trunk_widths = []
    for i, (xs, ys) in enumerate(trunks):
        L = len(xs)
        start_w = trunk_main_width if i == 0 else trunk_main_width / 2
        end_w = trunk_min_width if i == 0 else trunk_min_width / 2
        widths = np.linspace(start_w, end_w, L)
        trunk_widths.append(widths)

    branch_widths = []
    for _ in branches:
        branch_widths.append((branch_start, branch_end))

    return trunk_widths, branch_widths

# === 绘制带宽度的树形图像 ===
def draw_tree_with_widths(trunks, trunk_widths, branches, branch_widths, buds=None, leaves=None, filename="tree_filled.png"):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal')
    ax.axis('off')

    # 绘制 trunk
    for (xs, ys), ws in zip(trunks, trunk_widths):
        for i in range(1, len(xs)):
            ax.plot([xs[i-1], xs[i]], [ys[i-1], ys[i]], color='sienna', linewidth=ws[i-1])

    # 绘制 branch
    for ((x0, y0), (x1, y1)), (w0, w1) in zip(branches, branch_widths):
        ax.plot([x0, x1], [y0, y1], color='sienna', linewidth=(w0 + w1) / 2)

    # 绘制芽点
    if buds:
        for bud in buds:
            x, y = bud['pos']
            fate = bud['fate']
            if fate == 'grow':
                ax.plot(x, y, marker='^', color='orange', markersize=6)
            elif fate == 'flower':
                ax.plot(x, y, marker='*', color='red', markersize=6)
            elif fate == 'dormant':
                ax.plot(x, y, marker='o', color='gray', markersize=4)
            elif fate == 'abort':
                ax.plot(x, y, marker='x', color='black', markersize=4)

    # 绘制叶子
    if leaves:
        for x, y in leaves:
            ax.plot(x, y, marker='.', color='green', markersize=3)

    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"🌳 Tree rendered with widths to {filename}")

if __name__ == "__main__":
    trunks, buds, branches, leaves = import_tree_from_json("tree2.json")
    trunk_width, branch_width = assign_path_widths(trunks, branches)
    draw_tree_with_widths(trunks, trunk_width, branches, branch_width)
