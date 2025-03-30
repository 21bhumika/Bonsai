import numpy as np
import matplotlib.pyplot as plt

theta = np.linspace(0, np.pi, 100)
x1 = np.cos(theta)
y1 = np.sin(theta) * 2  # 拉长y轴

# 构造左右对称
x = np.concatenate((x1, -x1[::-1]))
y = np.concatenate((y1, y1[::-1]))

plt.plot(x, y, color='green')
plt.fill(x, y, color='lightgreen')
plt.axis('equal')
plt.title("Simple Elliptic Leaf")
plt.axis('off')
plt.show()
