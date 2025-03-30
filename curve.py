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
def plot_lines(lines, leaves, filename="probabilistic_tree.png"):
    fig, ax = plt.subplots(figsize=(10, 10))

    for (x0, y0), (x1, y1) in lines:
        ax.plot([x0, x1], [y0, y1], color="sienna", linewidth=0.8)

    for (lx, ly) in leaves:
        ax.plot(lx, ly, marker="o", color="green", markersize=2)

    ax.axis("equal")
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Tree image saved to {filename}")

# === 随机生成 Bézier 主干曲线并可视化 ===
def generate_random_control_points(n=None):
    if n is None:
        n = random.randint(5, 7)  # 增加控制点数提升复杂度
    ctrl_x = [0]
    ctrl_y = [0]
    angle = 90 + random.uniform(-5, 5)  # 起点基本朝上

    for i in range(1, n):
        if i == 1:
            # 第二点：强制明显向上
            delta_angle = random.uniform(-10, 10)
        else:
            # 之后允许大幅扭动
            delta_angle = random.uniform(-70, 70)
        angle += delta_angle
        length = random.uniform(25, 45)
        dx = math.cos(math.radians(angle)) * length
        dy = math.sin(math.radians(angle)) * length

        # 仅第一段强制向上，其余允许偏向但避免完全朝下
        if i == 1 and dy < 10:
            dy = 10 + abs(dy)

        ctrl_x.append(ctrl_x[-1] + dx)
        ctrl_y.append(ctrl_y[-1] + dy)

    return ctrl_x, ctrl_y

def draw_random_trunk_curve(filename="random_trunk_curve.png"):
    ctrl_x, ctrl_y = generate_random_control_points()
    k = min(3, len(ctrl_x) - 1)
    tck, u = splprep([ctrl_x, ctrl_y], s=0, k=k)
    u_fine = np.linspace(0, 1, 100)
    x_vals, y_vals = splev(u_fine, tck)

    plt.figure(figsize=(8, 8))
    plt.plot(ctrl_x, ctrl_y, 'ro--', label='Control Points')

    for i, (x, y) in enumerate(zip(ctrl_x, ctrl_y)):
        plt.text(x + 2, y + 2, f'P{i}', color='red', fontsize=10)

    plt.plot(x_vals, y_vals, color='sienna', linewidth=2, label='Bezier Curve')
    plt.axis('equal')
    plt.axis('off')
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Trunk curve saved to {filename}")

# === 主函数 ===
def main():
    draw_random_trunk_curve("random_trunk_curve.png")

if __name__ == "__main__":
    main()
