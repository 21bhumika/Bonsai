import random
import math
import re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from scipy.interpolate import splprep, splev
from util import import_tree_from_json

def draw_tree_canopy(ax, center, width, height, leaf_count=200):
    """在一个大椭圆区域内画多个小竖直椭圆作为叶子"""
    cx, cy = center

    # 画树冠范围（大椭圆）
    # canopy = Ellipse((cx, cy), width, height, angle=0, edgecolor='green', facecolor='lightgreen', alpha=0.3)
    # ax.add_patch(canopy)

    # 生成树叶（小椭圆）
    for _ in range(leaf_count):
        # 在大椭圆内部随机点，使用椭圆方程筛选
        while True:
            x = np.random.uniform(cx - width / 2, cx + width / 2)
            y = np.random.uniform(cy - height / 2, cy + height / 2)
            # 判断是否在椭圆内
            if ((x - cx) / (width / 2))**2 + ((y - cy) / (height / 2))**2 <= 1:
                break
        
        # 叶子的尺寸和下垂角度
        leaf_width = np.random.uniform(1.5, 3)
        leaf_height = np.random.uniform(4, 7)
        angle = np.random.normal(loc=180, scale=10)  # 接近垂直，稍有偏斜

        leaf = Ellipse((x, y), width=leaf_width, height=leaf_height, angle=angle,
                       color=random.choice(["#558172", "#96c49f"]), alpha=0.8)
        ax.add_patch(leaf)

def generate_leaf_cluster(center, count=4, radius=6, size_range=(5, 7), aspect_ratio=0.5):
    """生成一个叶子簇，整体朝下。"""
    cx, cy = center
    cluster = []
    for _ in range(count):
        angle = 270 + random.uniform(-30, 30)  # 朝下的小偏移
        r = random.uniform(0, radius)
        offset_angle = random.uniform(0, 2 * math.pi)
        dx = r * math.cos(offset_angle)
        dy = r * math.sin(offset_angle) * 0.5  # 稍微压扁成椭圆形分布
        leaf_center = (cx + dx, cy + dy)
        size = random.uniform(*size_range)
        cluster.append({
            "center": leaf_center,
            "angle": angle,
            "width": size,
            "height": size * aspect_ratio
        })
    return cluster


def collect_leaf_positions(buds, branch_trees):
    leaf_positions = []

    # 来自 bud 的花朵
    # for bud in buds:
    #     if bud['fate'] == 'flower':
    #         leaf_positions.append(bud['pos'])

    # 递归收集 branch_tree 的末端
    def dfs(node):

        # lebronlovers.us
        pts = node["points"]
        if not node["children"]:
            leaf_positions.append(tuple(pts[-1]))  # 终点
        for child in node["children"]:
            dfs(child)

    for tree in branch_trees:
        dfs(tree)

    return leaf_positions


from matplotlib.patches import Ellipse

def draw_elliptical_leaves(ax, leaf_positions, size_range=(8, 10), color_range=["#558172", "#96c49f"]):
    for (x, y) in leaf_positions:
        # leaf_cluster = generate_leaf_cluster((x, y))
        # for leaf in leaf_cluster:
        #     x, y = leaf["center"]
        #     angle = leaf["angle"]
        #     width = leaf["width"]
        #     height = leaf["height"]
        #     ellipse = plt.matplotlib.patches.Ellipse((x, y), width, height, angle=angle,
        #                                             color=random.choice(color_range), alpha=1, zorder=2)
        #     ax.add_patch(ellipse)
        draw_tree_canopy(ax, (x, y), width=60, height=25, leaf_count=100)

        # width = random.uniform(*size_range)
        # height = width * random.uniform(0.4, 0.7)  # 椭圆形状
        # angle = random.uniform(-60, 60)  # 旋转角度

        # color = random.choice(color_range)
        # leaf = Ellipse((x, y), width, height, angle=angle, color=color, alpha=0.75)
        # ax.add_patch(leaf)



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
        ax.plot([xs[i-1], xs[i]], [ys[i-1], ys[i]], color=color, linewidth=widths[i-1], zorder=1)

    # 获取末尾宽度用于子分支
    child_start_width = widths[-1]

    for child in branch_node.get("children", []):
        draw_branch_tree_recursive(child, child_start_width, ax, decay=decay, color=color)


# === 绘制带宽度的树形图像 ===
def draw_tree_with_widths(trunks, trunk_widths, branches, branch_widths, buds=None, leaves=None, filename="tree_filled.png"):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal')
    ax.axis('off')

    for (xs, ys), ws in zip(trunks, trunk_widths):
        segments = [([xs[i - 1], ys[i - 1]], [xs[i], ys[i]]) for i in range(1, len(xs))]
        lc = LineCollection(segments, linewidths=ws[:-1], colors="#43371f", capstyle='round', joinstyle='round')
        ax.add_collection(lc)

    for branch, start_width in zip(branches, branch_widths):
        draw_branch_tree_recursive(branch, start_width, ax)

    leaf_pos = collect_leaf_positions(buds, branches)
    draw_elliptical_leaves(ax, leaf_pos)

    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"🌳 Tree rendered with widths to {filename}")

from recur import draw_random_trunk_curve

if __name__ == "__main__":
    for i in range(10):

        trunks, buds, branches, leaves = draw_random_trunk_curve()
        trunk_width, branch_width = assign_path_widths(trunks, branches, trunk_main_width=60)
        draw_tree_with_widths(trunks, trunk_width, branches, branch_width, buds=buds, leaves=leaves, filename=f"pics/{str(i)}.png")
