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

# === 生成带反馈的 Bézier 主干曲线及芽点 ===
def generate_feedback_trunk_with_buds(n=6):
    ctrl_x = [0]
    ctrl_y = [0]
    angle = 90
    total_angle_change = 0

    for i in range(1, n):
        if i == 1:
            delta_angle = random.uniform(-10, 10)
        else:
            balance_bias = -0.2 * total_angle_change
            delta_angle = random.uniform(-40, 40) + balance_bias
        angle += delta_angle

        length = random.uniform(20, 40)
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

    # 插值曲线
    k = min(3, len(ctrl_x) - 1)
    tck, u = splprep([ctrl_x, ctrl_y], s=0, k=k)
    u_fine = np.linspace(0, 1, 100)
    x_vals, y_vals = splev(u_fine, tck)

    # 提取芽点
    buds = []
    for i in range(5, len(x_vals) - 1, 20):
        x, y = x_vals[i], y_vals[i]
        dx = x_vals[i+1] - x_vals[i-1]
        dy = y_vals[i+1] - y_vals[i-1]
        angle = math.degrees(math.atan2(dy, dx))
        fate = random.choices(['grow', 'flower', 'dormant', 'abort'], [0.4, 0.2, 0.3, 0.1])[0]
        buds.append({ 'pos': (x, y), 'angle': angle, 'fate': fate })

    return x_vals, y_vals, buds

def draw_random_trunk_curve(filename="random_trunk_curve.png"):
    x_vals, y_vals, buds = generate_feedback_trunk_with_buds()

    plt.figure(figsize=(8, 8))
    plt.plot(x_vals, y_vals, color='sienna', linewidth=2, label='Bezier Curve')

    for bud in buds:
        x, y = bud['pos']
        fate = bud['fate']
        if fate == 'grow':
            plt.plot(x, y, marker='^', color='orange', markersize=10)
        elif fate == 'flower':
            plt.plot(x, y, marker='*', color='red', markersize=10)
        elif fate == 'dormant':
            plt.plot(x, y, marker='o', color='gray', markersize=10)
        elif fate == 'abort':
            plt.plot(x, y, marker='x', color='black', markersize=10)

    plt.axis('equal')
    plt.axis('off')
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Trunk curve with buds saved to {filename}")

# === 主函数 ===
def main():
    draw_random_trunk_curve("random_trunk_with_buds.png")

if __name__ == "__main__":
    main()
