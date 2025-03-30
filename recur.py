import random
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev
from util import export_tree_to_json

all_trunk_segments = []
all_branch_trees = []
all_leaves = []


def grow_branch_tree_list(start_pos, angle, depth, ratio, is_top_branch, max_depth=3, base_step=14, angle_range=(-30, 30)):
    if depth > max_depth:
        return None

    x, y = start_pos
    current_angle = angle
    points = [(x, y)]
    is_crown = False
    if is_top_branch and ratio > 0.75: 
        
        # crown type
        scale = 0.1
        is_crown = True
        current_angle = 90 + random.uniform(-20, 20)

    else:
        # the further the shorter
        scale = 0.5 ** (depth - 1)
    
    local_step_range = (base_step * 0.5 * scale, base_step * 1.0 * scale)

    n_segments = random.randint(2, 4) if not is_crown else 1
    for _ in range(n_segments):
        step = random.uniform(*local_step_range)
        rad = math.radians(current_angle)
        x += step * math.cos(rad)
        y += step * math.sin(rad)
        points.append((x, y))
        current_angle += random.uniform(-10, 10)

    node = {
        "points": [[float(px), float(py)] for px, py in points],
        "children": []
    }

    for i in range(len(points) - 2, len(points)):
        if depth < max_depth and (i == len(points) - 1 or random.random() < 0.3):
            if is_crown:
                branch_count = random.randint(2, 3)
            else:
                branch_count = random.randint(1, 2)

            
            for _ in range(branch_count):
                if is_crown:
                    branch_angle = random.randint(0, 180) + random.uniform(*angle_range)
                else:
                    branch_angle = current_angle + random.uniform(*angle_range)
                child = grow_branch_tree_list(points[i], branch_angle, depth + 1, 0, False, max_depth, base_step, angle_range)
                if child:
                    node["children"].append(child)

    return node

def generate_trunk_curve(n=6, start_pos=(0, 0), start_angle=90, length_range=(20, 40)):
    ctrl_x = [start_pos[0]]
    ctrl_y = [start_pos[1]]
    angle = start_angle
    total_angle_change = 0

    for i in range(1, n):
        if i == 1:
            delta_angle = random.uniform(-30, 30)
        else:
            balance_bias = -0.2 * total_angle_change
            delta_angle = random.uniform(-40, 40) + balance_bias * 0.5
        angle += delta_angle

        length = random.uniform(*length_range)
        dx = math.cos(math.radians(angle)) * length
        dy = math.sin(math.radians(angle)) * length
        if i == 1 and dy < 10:
            dy = 10 + abs(dy)

        ctrl_x.append(ctrl_x[-1] + dx)
        ctrl_y.append(ctrl_y[-1] + dy)

        if i >= 2:
            dx1 = ctrl_x[-2] - ctrl_x[-3]
            dy1 = ctrl_y[-2] - ctrl_y[-3]
            ang1 = math.atan2(dy1, dx1)
            ang2 = math.atan2(dy, dx)
            dtheta = math.degrees(ang2 - ang1)
            while dtheta > 180: dtheta -= 360
            while dtheta < -180: dtheta += 360
            total_angle_change += dtheta

    if len(ctrl_x) < 2:
        return np.array([]), np.array([])

    k = min(3, len(ctrl_x) - 1)
    tck, u = splprep([ctrl_x, ctrl_y], s=0, k=k)
    u_fine = np.linspace(0, 1, 150)
    return splev(u_fine, tck)

def generate_feedback_trunk_with_buds(n=6, start_pos=(0, 0), start_angle=90, length_range=(20, 40)):
    global all_trunk_segments

    
    ctrl_x = [start_pos[0]]
    ctrl_y = [start_pos[1]]
    angle = start_angle
    total_angle_change = 0

    for i in range(1, n):
        if i == 1:
            delta_angle = random.uniform(-30, 30)
        else:
            balance_bias = -0.2 * total_angle_change
            delta_angle = random.uniform(-40, 40) + balance_bias * 0.5
        angle += delta_angle

        length = random.uniform(*length_range)
        dx = math.cos(math.radians(angle)) * length
        dy = math.sin(math.radians(angle)) * length
        if i == 1 and dy < 10:
            dy = 10 + abs(dy)

        ctrl_x.append(ctrl_x[-1] + dx)
        ctrl_y.append(ctrl_y[-1] + dy)

        if i >= 2:
            dx1 = ctrl_x[-2] - ctrl_x[-3]
            dy1 = ctrl_y[-2] - ctrl_y[-3]
            ang1 = math.atan2(dy1, dx1)
            ang2 = math.atan2(dy, dx)
            dtheta = math.degrees(ang2 - ang1)
            while dtheta > 180: dtheta -= 360
            while dtheta < -180: dtheta += 360
            total_angle_change += dtheta

    if len(ctrl_x) < 2:
        return [], [], []
    k = min(3, len(ctrl_x) - 1)
    tck, u = splprep([ctrl_x, ctrl_y], s=0, k=k)
    u_fine = np.linspace(0, 1, 150)
    x_vals, y_vals = splev(u_fine, tck)

    buds = []

    grow_limit = random.randint(3, 6)
    grow_count = 0
    sub_trunk_limit = random.randint(1, 2)
    sub_trunk_count = 0
    last_grow_pos = None

    min_dist_between_grows = len(x_vals) // (grow_limit + 1)

    for i in range(len(x_vals) - 2, 4, -10):
        x, y = x_vals[i], y_vals[i]
        dx = x_vals[i+1] - x_vals[i-1]
        dy = y_vals[i+1] - y_vals[i-1]
        angle = math.degrees(math.atan2(dy, dx))

        fate = None
        ratio = float(i / len(x_vals))
        if grow_count < grow_limit:
            if last_grow_pos is None or last_grow_pos - i >= min_dist_between_grows:
                if random.random() < 0.6:
                    fate = 'grow'
                    grow_count += 1
                    last_grow_pos = i
        fate = random.choices(['flower', 'dormant', 'abort'], [0.1, 0.7, 0.2])[0] if fate == None else fate
            
        buds.append({ 'pos': (x, y), 'angle': angle, 'fate': fate , 'ratio': ratio})
        if fate == 'grow':
            if random.random() < 0.8 and sub_trunk_count < sub_trunk_limit and ratio < 0.6:
                
                # the further the shorter
                remaining = (i / len(x_vals))  
                sub_n = max(3, int(n * remaining * 1.5))
                sub_x, sub_y = generate_trunk_curve(
                    n=sub_n,
                    start_pos=(x, y),
                    start_angle=angle + random.uniform(-40, 40),
                    length_range=(20, 40)
                )
                if len(sub_x) > 0 and len(sub_y) > 0:
                    if len(sub_x) > 0:
                        all_trunk_segments.append((sub_x, sub_y))

                        sub_buds = []
                        sub_grow_limit = random.randint(0, 3)
                        sub_grow_count = 0
                        last_sub_grow_pos = None
                        min_sub_dist = len(sub_x) // (sub_grow_limit + 1)

                        for j in range(len(sub_x) - 2, 4, -20):
                            sx, sy = sub_x[j], sub_y[j]
                            sdx = sub_x[j+1] - sub_x[j-1]
                            sdy = sub_y[j+1] - sub_y[j-1]
                            s_angle = math.degrees(math.atan2(sdy, sdx))

                            sub_fate = None
                            if sub_grow_count < sub_grow_limit:
                                if last_sub_grow_pos is None or last_sub_grow_pos - j >= min_sub_dist:
                                    if random.random() < 0.6:
                                        sub_fate = 'grow'
                                        sub_grow_count += 1
                                        last_sub_grow_pos = j
                            sub_fate = random.choices(['flower', 'dormant', 'abort'], [0.1, 0.7, 0.2])[0] if sub_fate is None else sub_fate
                            sub_buds.append({ 'pos': (sx, sy), 'angle': s_angle, 'fate': sub_fate, 'ratio': float(j / len(sub_x))})

                        buds.extend(sub_buds)
                    sub_trunk_count += 1
            elif random.random() < 0.5:
                
                # double fork
                buds.append({ 'pos': (x, y), 'angle': angle, 'fate': fate, 'ratio': ratio})

    all_trunk_segments.append((x_vals, y_vals))
    return x_vals, y_vals, buds

def draw_random_trunk_curve(filename):
    global all_trunk_segments, all_branch_trees, all_leaves
    all_trunk_segments = []
    all_branch_trees = []
    all_leaves = []

    # generate the main trunk here
    x_vals, y_vals, all_buds = generate_feedback_trunk_with_buds(n=6)

    # grow branches
    for bud in all_buds:
        if bud['fate'] == 'grow':
            
            # almost horizontal
            base_angle = bud['angle'] + random.choice([-90, 90])  # 垂线方向
            jitter = random.uniform(-40, 40)
            side_angle = base_angle + jitter

            if 210 <= side_angle <= 340:
                side_angle = random.randint(20, 160) + jitter

            branch_tree = grow_branch_tree_list(
                start_pos=bud['pos'],
                angle=side_angle,
                depth=1,
                max_depth=3,
                ratio=bud['ratio'],
                is_top_branch=True
            )
            if branch_tree:
                all_branch_trees.append(branch_tree)


    plt.figure(figsize=(8, 8))

    for (x, y) in all_trunk_segments:
        plt.plot(x, y, color='sienna', linewidth=1.5)

    plt.plot(x_vals[0], y_vals[0], marker='s', color='blue', markersize=6, label='Start Point')

    def draw_branch_skeleton(branch_node):
        pts = branch_node["points"]
        for i in range(1, len(pts)):
            x0, y0 = pts[i-1]
            x1, y1 = pts[i]
            plt.plot([x0, x1], [y0, y1], color='peru', linewidth=1)

        for child in branch_node.get("children", []):
            draw_branch_skeleton(child)

    for tree in all_branch_trees:
        draw_branch_skeleton(tree)


    for bud in all_buds:
        x, y = bud['pos']
        fate = bud['fate']
        if fate == 'grow':
            plt.plot(x, y, marker='^', color='orange', markersize=12)
        elif fate == 'flower':
            plt.plot(x, y, marker='*', color='red', markersize=4)
        elif fate == 'dormant':
            plt.plot(x, y, marker='o', color='gray', markersize=3)
        elif fate == 'abort':
            plt.plot(x, y, marker='x', color='black', markersize=2)

    for bx, by in all_leaves:
        plt.plot(bx, by, marker='.', color='green', markersize=3)

    plt.axis('equal')
    plt.axis('off')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"pics/ske_{str(filename)}.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Tree skeleton saved to {filename}")
    export_tree_to_json(f"pics/ske_{str(filename)}.json", all_trunk_segments[::-1], all_buds[::-1], all_branch_trees[::-1], all_leaves[::-1])
    return all_trunk_segments[::-1], all_buds[::-1], all_branch_trees[::-1], all_leaves[::-1]

if __name__ == "__main__":
    draw_random_trunk_curve()