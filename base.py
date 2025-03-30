import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import random

def draw_base(filename="bonsai_base.png"):
    base_type = random.choice(["cuboid", "trapezoidal", "cylinder"])
    print(f"Base type selected: {base_type}")
    
    if base_type == "cylinder":
        draw_3D_base(filename)
    else:
        draw_flat_base(filename, base_type)

def draw_3D_base(filename):
    fig = plt.figure(figsize=(6, 4))
    ax = fig.add_subplot(111, projection='3d')
    ax.axis('off')

    height = random.uniform(0.5, 2.0)
    width = random.uniform(4.0, 8.0)
    depth = random.uniform(2.0, 4.0)

    r_top = random.uniform(0.5, 1.0) * (width / 2)
    r_bot = width / 2
    z = np.linspace(0, height, 30)
    theta = np.linspace(0, 2 * np.pi, 50)
    Z, Theta = np.meshgrid(z, theta)

    R = np.linspace(r_bot, r_top, len(z))
    R = np.tile(R, (len(theta), 1))
    X = R * np.cos(Theta)
    Y = R * np.sin(Theta)

    ax.plot_surface(
        X, Y, Z,
        color='gray',
        edgecolor='none',
        linewidth=0,
        antialiased=True,
        alpha=1.0
    )

    ax.set_box_aspect([width, depth, height])
    ax.view_init(elev=15, azim=0)
    ax.set_axis_off()
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, transparent=True)
    plt.close()
    print(f"Base saved to: {filename}")


def draw_flat_base(filename, base_type):
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.set_aspect('equal')
    ax.axis('off')

    width = random.uniform(6, 8)
    height = random.uniform(2, 3)
    top_depth = random.uniform(0.3, 0.5)
    top_shrink = random.uniform(0.7, 0.9)
    corner_radius = min(0.6, height * 0.25)

    # Base front face vertices
    if base_type == "trapezoidal":
        shrink = random.uniform(0.5, 0.9)
        top_right = (width * shrink + (1 - shrink) * width / 2, height)
        top_left = ((1 - shrink) * width / 2, height)
    else:
        top_left = (0, height)
        top_right = (width, height)

    bottom_left = (0, 0)
    bottom_right = (width, 0)

    # Rounded front face: simulated with straight edges and corner arcs
    def arc(cx, cy, start_angle, end_angle, r, steps=6):
        angles = np.linspace(start_angle, end_angle, steps)
        return [(cx + r * np.cos(a), cy + r * np.sin(a)) for a in angles]

    # Points with arcs replacing corners
    front_face = []
    front_face += arc(bottom_left[0] + corner_radius, bottom_left[1] + corner_radius, np.pi, 1.5*np.pi, corner_radius)
    front_face.append((bottom_right[0] - corner_radius, bottom_right[1]))
    front_face += arc(bottom_right[0] - corner_radius, bottom_right[1] + corner_radius, 1.5*np.pi, 2*np.pi, corner_radius)
    front_face.append((top_right[0], top_right[1] - corner_radius))
    front_face += arc(top_right[0] - corner_radius, top_right[1] - corner_radius, 0, 0.5*np.pi, corner_radius)
    front_face.append((top_left[0] + corner_radius, top_left[1]))
    front_face += arc(top_left[0] + corner_radius, top_left[1] - corner_radius, 0.5*np.pi, np.pi, corner_radius)
    front_face.append((bottom_left[0], bottom_left[1] + corner_radius))

    ax.add_patch(patches.Polygon(front_face, closed=True, facecolor="gray", edgecolor="black", linewidth=2))

    # ✅ Adjusted top face: start inside the corners
    adjusted_left = top_left[0] + corner_radius
    adjusted_right = top_right[0] - corner_radius

    top_inner_left = (
        adjusted_left + (adjusted_right - adjusted_left) * (1 - top_shrink) / 2,
        top_left[1] + top_depth
    )
    top_inner_right = (
        adjusted_right - (adjusted_right - adjusted_left) * (1 - top_shrink) / 2,
        top_right[1] + top_depth
    )

    top_face = [
        (adjusted_left, top_left[1]),
        (adjusted_right, top_right[1]),
        top_inner_right,
        top_inner_left
    ]
    ax.add_patch(patches.Polygon(top_face, closed=True, facecolor="#cccccc", edgecolor="black", linewidth=2))

    ax.set_xlim(-1, width + 2)
    ax.set_ylim(-1, height + top_depth + 1)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, transparent=True)
    plt.close()
    print(f"Flat base saved to: {filename}")
