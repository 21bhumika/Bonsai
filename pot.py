import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import random
import math
import os

import matplotlib.pyplot as plt
import numpy as np
import random

def generate_profile_points():
    # 花盆右半边的轮廓线（对称轴为 y）
    h = random.uniform(1.2, 2.0)   # 高度
    w = random.uniform(0.6, 1.0)   # 最宽处半宽
    neck = random.uniform(0.3, 0.6)  # 盆口收紧程度
    base = random.uniform(0.2, 0.4)  # 底座宽度
    belly = random.uniform(0.7, 1.0) # 胯部膨胀位置占比
    
    # 4个轮廓关键点：底 → 胯 → 脖子 → 口
    points = [
        (0, 0),                          # 底部中心
        (base, h * 0.05),               # 小底圈
        (w, h * belly),                 # 最大胯部
        (neck, h * 0.95),              # 收口脖子
        (w * 0.95, h)                  # 开口边缘
    ]

    # 插值为平滑曲线
    x, y = zip(*points)
    t = np.linspace(0, 1, 100)
    x_interp = np.interp(t, np.linspace(0, 1, len(x)), x)
    y_interp = np.interp(t, np.linspace(0, 1, len(y)), y)
    
    # 添加手工感的扰动
    noise_strength = 0.02
    x_interp += np.random.normal(0, noise_strength, size=len(x_interp))

    return x_interp, y_interp

def draw_pot(ax, offset_x=0, offset_y=0, color="#c68642"):
    x, y = generate_profile_points()
    # 构造左右两边轮廓（对称）
    full_x = np.concatenate([x[::-1] * -1, x])
    full_y = np.concatenate([y[::-1], y])
    
    ax.fill(full_x + offset_x, full_y + offset_y, color=color, linewidth=0, zorder=2)
    # 投影阴影感
    ax.fill(full_x + offset_x + 0.05, full_y + offset_y - 0.05, color='black', alpha=0.1, zorder=1)

def generate_batch_pots(count=6, filename="nicer_pots.png"):
    fig, ax = plt.subplots(figsize=(count * 2, 4))
    ax.set_xlim(0, count * 2)
    ax.set_ylim(0, 3)
    ax.axis('off')

    for i in range(count):
        color = random.choice(["#c68642", "#a87c56", "#8b5e3c", "#d2b48c", "#5c4433"])
        draw_pot(ax, offset_x=i * 2 + 1, offset_y=0.2, color=color)

    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close(fig)
    print(f"✅ Saved: {filename}")

if __name__ == "__main__":
    generate_batch_pots()