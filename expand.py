import random
import math
import re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from scipy.interpolate import splprep, splev
from util import import_tree_from_json

# === 给 trunk 和 branch 路径添加宽度 ===
def assign_path_widths(trunks, branch_trees, trunk_main_width=50, trunk_min_width=1):
    trunk_widths = []
    for i, (xs, ys) in enumerate(trunks):
        L = len(xs)
        start_w = trunk_main_width if i == 0 else trunk_main_width / 2
        end_w = trunk_min_width if i == 0 else trunk_min_width / 2
        widths = np.linspace(start_w, end_w, L)
        trunk_widths.append(widths)

    # 构造芽点位置 → trunk 宽度的映射
    width_map = {}
    for (xs, ys), ws in zip(trunks, trunk_widths):
        for i in range(len(xs)):
            key = (round(xs[i], 2), round(ys[i], 2))
            width_map[key] = ws[i]

    # 为顶级分支赋予起始宽度（供后续绘制时衰减）
    branch_start_widths = []
    for tree in branch_trees:
        x0, y0 = tree["points"][0]
        key = (round(x0, 2), round(y0, 2))
        start_width = min(10, width_map.get(key, 10) // 2)
        branch_start_widths.append(start_width)

    return trunk_widths, branch_start_widths


def draw_branch_tree_recursive(branch_node, start_width, ax, decay=0.7, color='#43371f'):
    points = branch_node["points"]
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    L = len(xs)

    # 从 start_width 衰减到 start_width * decay
    end_width = start_width * decay
    widths = np.linspace(start_width, end_width, L)

    # 绘制主分支线条
    for i in range(1, L):
        ax.plot([xs[i-1], xs[i]], [ys[i-1], ys[i]], color=color, linewidth=widths[i-1])

    # 获取末尾宽度用于子分支
    child_start_width = widths[-1]

    for child in branch_node.get("children", []):
        draw_branch_tree_recursive(child, child_start_width, ax, decay=decay, color=color)


# === 绘制带宽度的树形图像 ===
def draw_tree_with_widths(trunks, trunk_widths, branches, branch_widths, buds=None, leaves=None, filename="tree_filled.png"):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal')
    ax.axis('off')

    # 绘制 trunk
    for (xs, ys), ws in zip(trunks, trunk_widths):
        for i in range(1, len(xs)):
            ax.plot([xs[i-1], xs[i]], [ys[i-1], ys[i]], color="#43371f", linewidth=ws[i-1])

    for branch, start_width in zip(branches, branch_widths):
        draw_branch_tree_recursive(branch, start_width, ax)

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
            if random.random() < 0.5:
                ax.plot(x, y, marker='.', color='#598576', markersize=40, alpha=0.6)
            else:  
                ax.plot(x, y, marker='.', color='#97c69c', markersize=40, alpha=0.6)

    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"🌳 Tree rendered with widths to {filename}")

from recur import draw_random_trunk_curve

if __name__ == "__main__":
    # trunks, buds, branches, leaves = draw_random_trunk_curve()
    # trunk_width, branch_width = assign_path_widths(trunks, branches, trunk_main_width=60)
    # draw_tree_with_widths(trunks, trunk_width, branches, branch_width, leaves=leaves, filename=f"pics/{str(11)}.png")
    for i in range(10):

        trunks, buds, branches, leaves = draw_random_trunk_curve()
        trunk_width, branch_width = assign_path_widths(trunks, branches, trunk_main_width=60)
        draw_tree_with_widths(trunks, trunk_width, branches, branch_width, leaves=leaves, filename=f"pics/{str(i)}.png")
