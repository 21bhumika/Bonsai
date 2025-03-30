import random
import math
import re
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev

# === 随机规则选择器 ===
def choose_rule(ruleset):
    if isinstance(ruleset, list):
        r = random.random()
        acc = 0
        for rule, prob in ruleset:
            acc += prob
            if r < acc:
                return rule
        return ruleset[-1][0]  # fallback
    return ruleset

# === 支持概率的 L-System 替换器 ===
def expand_lsystem(start, rules, depth):
    result = start
    for _ in range(depth):
        next_result = ""
        for ch in result:
            if ch in rules:
                replacement = choose_rule(rules[ch])
                next_result += replacement
            else:
                next_result += ch
        result = next_result
    return result

# === 命令解析器（支持带角度） ===
def parse_command(cmd):
    pattern = r'([Ff\+\-\[\]L])([0-9]{0,3})'
    parsed = []
    for match in re.finditer(pattern, cmd):
        symbol, value = match.groups()
        parsed.append((symbol, float(value) if value else None))
    return parsed

# === 绘图器 ===
def draw_l_system(parsed_cmd, default_angle=25, step=6):
    x, y = 0.0, 0.0
    angle = 90
    stack = []
    lines = []
    leaves = []

    for cmd, val in parsed_cmd:
        if cmd == "F":
            rad = math.radians(angle)
            x_new = x + step * math.cos(rad)
            y_new = y + step * math.sin(rad)
            lines.append(((x, y), (x_new, y_new)))
            x, y = x_new, y_new
        elif cmd == "L":
            leaves.append((x, y))
        elif cmd == "+":
            angle += val if val is not None else default_angle
        elif cmd == "-":
            angle -= val if val is not None else default_angle
        elif cmd == "[":
            stack.append((x, y, angle))
        elif cmd == "]":
            x, y, angle = stack.pop()

    return lines, leaves

# === 绘制输出 ===
def plot_lines(lines, leaves, buds, filename="probabilistic_tree.png"):
    fig, ax = plt.subplots(figsize=(10, 10))

    for (x0, y0), (x1, y1) in lines:
        ax.plot([x0, x1], [y0, y1], color="sienna", linewidth=0.8)

    for (lx, ly) in leaves:
        ax.plot(lx, ly, marker="o", color="green", markersize=2)

    # 标注芽点
    for bud in buds:
        x, y = bud['pos']
        fate = bud['fate']
        if fate == 'grow':
            ax.plot(x, y, marker='^', color='orange', markersize=4)
        elif fate == 'flower':
            ax.plot(x, y, marker='*', color='red', markersize=4)
        elif fate == 'dormant':
            ax.plot(x, y, marker='o', color='gray', markersize=3)
        elif fate == 'abort':
            ax.plot(x, y, marker='x', color='black', markersize=2)

    ax.axis("equal")
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Tree image saved to {filename}")

all_trunk_segments = []

# === 局部扰动方式（嵌入式波动） ===
def distort_curve(x_vals, y_vals, scale=15, frequency=5):
    distorted_x = []
    distorted_y = []
    for i in range(len(x_vals)):
        t = i / len(x_vals)
        amp = scale * (1 - t**0.5)
        wave = math.sin(t * math.pi * frequency) * amp
        normal_dx = y_vals[min(i+1, len(y_vals)-1)] - y_vals[max(i-1, 0)]
        normal_dy = -(x_vals[min(i+1, len(x_vals)-1)] - x_vals[max(i-1, 0)])
        norm_len = math.hypot(normal_dx, normal_dy) + 1e-6
        nx = normal_dx / norm_len
        ny = normal_dy / norm_len
        distorted_x.append(x_vals[i] + wave * nx)
        distorted_y.append(y_vals[i] + wave * ny)

    return distorted_x, distorted_y

# === 主干生成函数（支持初始位置与方向） ===
def generate_feedback_trunk_with_buds(n=6, start_pos=(0, 0), start_angle=90, length_range=(20, 40)):
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

    k = min(3, len(ctrl_x) - 1)
    tck, u = splprep([ctrl_x, ctrl_y], s=0, k=k)
    u_fine = np.linspace(0, 1, 150)
    x_vals, y_vals = splev(u_fine, tck)
    x_vals, y_vals = distort_curve(x_vals, y_vals, scale=15, frequency=5)

    buds = []
    for i in range(5, len(x_vals) - 1, 10):
        x, y = x_vals[i], y_vals[i]
        dx = x_vals[i+1] - x_vals[i-1]
        dy = y_vals[i+1] - y_vals[i-1]
        angle = math.degrees(math.atan2(dy, dx))
        fate = random.choices(['grow', 'flower', 'dormant', 'abort'], [0.4, 0.2, 0.3, 0.1])[0]
        buds.append({ 'pos': (x, y), 'angle': angle, 'fate': fate })

    all_trunk_segments.append((x_vals, y_vals))
    return x_vals, y_vals, buds

# === 递归主干生长 ===
def grow_recursive_trunk(start_pos, start_angle, depth, max_depth=3):
    if depth > max_depth:
        return []
    base_n = min(3, 6 - depth)
    base_range = (15, 30) if depth > 1 else (25, 45)
    x_vals, y_vals, buds = generate_feedback_trunk_with_buds(
        n=base_n, start_pos=start_pos, start_angle=start_angle, length_range=base_range
    )
    all_buds = list(buds)
    grow_buds = [b for b in buds if b['fate'] == 'grow']
    for b in random.sample(grow_buds, min(2, len(grow_buds))):
        sub_b = grow_recursive_trunk(b['pos'], b['angle'], depth + 1, max_depth)
        all_buds += sub_b
    return all_buds

# === 主函数 ===
def draw_random_trunk_curve(filename="recursive_trunk_tree.png"):
    global all_trunk_segments
    all_trunk_segments = []
    all_buds = grow_recursive_trunk((0, 0), 90, depth=1, max_depth=1)

    plt.figure(figsize=(8, 8))
    for idx, (x, y) in enumerate(all_trunk_segments):
        plt.plot(x, y, color='sienna', linewidth=1.5)
    plt.plot(all_trunk_segments[0][0][0], all_trunk_segments[0][1][0], marker='s', color='blue', markersize=6, label='Start Point')

    for bud in all_buds:
        x, y = bud['pos']
        fate = bud['fate']
        if fate == 'grow':
            plt.plot(x, y, marker='^', color='orange', markersize=4)
        elif fate == 'flower':
            plt.plot(x, y, marker='*', color='red', markersize=4)
        elif fate == 'dormant':
            plt.plot(x, y, marker='o', color='gray', markersize=3)
        elif fate == 'abort':
            plt.plot(x, y, marker='x', color='black', markersize=2)

    plt.axis('equal')
    plt.axis('off')
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"🌲 Recursive tree saved to {filename}")

if __name__ == "__main__":
    draw_random_trunk_curve()