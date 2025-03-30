import random
import math
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from colors import trunk_colors, leaves_colors, plant_pot_colors
from pot import draw_plant_pot
from recur import draw_random_trunk_curve
from flower import gen_params, draw_flower_at


def draw_tree_canopy(ax, center, width, height, leaf_color, leaf_count=200):
    cx, cy = center

    for _ in range(leaf_count):
        while True:
            x = np.random.uniform(cx - width / 2, cx + width / 2)
            y = np.random.uniform(cy - height / 2, cy + height / 2)
            if ((x - cx) / (width / 2))**2 + ((y - cy) / (height / 2))**2 <= 1:
                break
        
        leaf_width = np.random.uniform(1.5, 3)
        leaf_height = np.random.uniform(4, 7)
        angle = np.random.normal(loc=180, scale=10)

        leaf = Ellipse((x, y), width=leaf_width, height=leaf_height, angle=angle,
                       color=random.choice(leaf_color), alpha=0.8)
        ax.add_patch(leaf)

def draw_flowers_canopy(ax, center, width, height, leaf_color, flower_count=12):
    cx, cy = center

    for _ in range(flower_count):
        while True:
            x = np.random.uniform(cx - width / 2, cx + width / 2)
            y = np.random.uniform(cy - height / 2, cy + height / 2)
            if ((x - cx) / (width / 2))**2 + ((y - cy) / (height / 2))**2 <= 1:
                break

        angle = np.random.uniform(0, 360)   
        scale = np.random.uniform(2.2, 3.0)
        PAR = gen_params(leaf_palette=leaf_color)

        # Reduce opacity (0.25–0.45) to make flowers more transparent
        PAR["flowerColor"]["min"][3] = np.random.uniform(0.65, 0.85) 

        draw_flower_at(ax, x, y, angle, PAR, scale=scale)

def generate_leaf_cluster(center, count=4, radius=6, size_range=(5, 7), aspect_ratio=0.5):
    cx, cy = center
    cluster = []
    for _ in range(count):
        angle = 270 + random.uniform(-30, 30)
        r = random.uniform(0, radius)
        offset_angle = random.uniform(0, 2 * math.pi)
        dx = r * math.cos(offset_angle)
        dy = r * math.sin(offset_angle) * 0.5
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
    def dfs(node):
        pts = node["points"]
        if not node["children"]:
            leaf_positions.append(tuple(pts[-1]))
        for child in node["children"]:
            dfs(child)

    for tree in branch_trees:
        dfs(tree)

    return leaf_positions


from matplotlib.patches import Ellipse

def draw_elliptical_leaves(ax, leaf_positions, leaf_color):
    for (x, y) in leaf_positions:
        draw_tree_canopy(ax, (x, y), width=60, height=25, leaf_color=leaf_color, leaf_count=50)

def draw_flowers_at_leaves(ax, leaf_positions, leaf_color):
    for (x, y) in leaf_positions:
        draw_flowers_canopy(ax, (x, y), width=60, height=25, leaf_color=leaf_color, flower_count=50)


def assign_path_widths(trunks, branch_trees, trunk_main_width=50, trunk_min_width=1):
    trunk_widths = []
    for i, (xs, ys) in enumerate(trunks):
        L = len(xs)
        start_w = trunk_main_width if i == 0 else trunk_main_width / 2
        end_w = trunk_min_width if i == 0 else trunk_min_width / 2
        widths = np.linspace(start_w, end_w, L)
        trunk_widths.append(widths)

    width_map = {}
    for (xs, ys), ws in zip(trunks, trunk_widths):
        for i in range(len(xs)):
            key = (round(xs[i], 2), round(ys[i], 2))
            width_map[key] = ws[i]

    branch_start_widths = []
    for tree in branch_trees:
        x0, y0 = tree["points"][0]
        key = (round(x0, 2), round(y0, 2))
        start_width = min(10, width_map.get(key, 10) // 2)
        branch_start_widths.append(start_width)

    return trunk_widths, branch_start_widths


def draw_branch_tree_recursive(branch_node, start_width, ax, color, decay=0.7):
    points = branch_node["points"]
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    L = len(xs)

    end_width = start_width * decay
    widths = np.linspace(start_width, end_width, L)

    for i in range(1, L):
        ax.plot([xs[i-1], xs[i]], [ys[i-1], ys[i]], color=color, linewidth=widths[i-1], zorder=1)

    child_start_width = widths[-1]

    for child in branch_node.get("children", []):
        draw_branch_tree_recursive(child, child_start_width, ax, decay=decay, color=color)


use_flowers = random.random() < 0.5 
def draw_tree_with_widths(trunks, trunk_widths, branches, branch_widths, buds=None, leaves=None, filename="tree_filled.png", trunk_color=["#43371f"], leaf_color=["#558172", "#96c49f"], pot_color=["4f4c5d"], use_flowers=use_flowers):
    _, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal')
    ax.axis('off')

    root = (trunks[0][0][0], trunks[0][1][0])
    selected_pot_color = random.choice(pot_color)
    draw_plant_pot(ax, root[0], root[1] - 17, pot_color=selected_pot_color)


    selected_trunk_color = random.choice(trunk_color)
    for (xs, ys), ws in zip(trunks, trunk_widths):
        segments = [([xs[i - 1], ys[i - 1]], [xs[i], ys[i]]) for i in range(1, len(xs))]
        lc = LineCollection(segments, linewidths=ws[:-1], colors=selected_trunk_color, capstyle='round', joinstyle='round')
        ax.add_collection(lc)

    for branch, start_width in zip(branches, branch_widths):
        draw_branch_tree_recursive(branch, start_width, ax, color=selected_trunk_color)

    leaf_pos = collect_leaf_positions(buds, branches)
    if use_flowers:
        draw_flowers_at_leaves(ax, leaf_pos, leaf_color)
    else:
        draw_elliptical_leaves(ax, leaf_pos, leaf_color)

    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Tree rendered to {filename}")

if __name__ == "__main__":
    for i in range(50):
        os.makedirs("pics", exist_ok=True)
        cur_trunk_color, cur_leaf_color, cur_pot_color = \
            random.choice(trunk_colors), random.choice(leaves_colors), random.choice(plant_pot_colors)
        trunks, buds, branches, leaves = draw_random_trunk_curve(i)
        trunk_width, branch_width = assign_path_widths(trunks, branches, trunk_main_width=60)
        draw_tree_with_widths(trunks, trunk_width, branches, branch_width, buds=buds, leaves=leaves, filename=f"pics/{str(i)}.png", trunk_color=cur_trunk_color, leaf_color=cur_leaf_color, pot_color=cur_pot_color)
