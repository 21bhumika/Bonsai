import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import random

def draw_base(filename="bonsai_base.png"):
    base_type = random.choice(["cuboid", "trapezoidal", "cylinder", "curved trapezoidal", "spherical"])
    print(f"Base type selected: {base_type}")
    
    add_feet = random.random() < 0.5
    if base_type == "cylinder":
        draw_3D_base(filename, base_type)
    elif base_type == "spherical":
        draw_3D_base(filename, base_type)
    else:
        draw_flat_base(filename, base_type, add_feet)

def draw_3D_base(filename, base_type):
    fig = plt.figure(figsize=(6, 4))
    ax = fig.add_subplot(111, projection='3d')
    ax.axis('off')

    height = random.uniform(0.5, 2.0)
    width = random.uniform(4.0, 8.0)
    depth = random.uniform(2.0, 4.0)

    if base_type == "cylinder":
        r_top = random.uniform(0.5, 1.0) * (width / 2)
        r_bot = width / 2
        z = np.linspace(0, height, 30)
        theta = np.linspace(0, 2 * np.pi, 50)
        Z, Theta = np.meshgrid(z, theta)

        R = np.linspace(r_bot, r_top, len(z))
        R = np.tile(R, (len(theta), 1))
        X = R * np.cos(Theta) + width / 2    # shift X to [0, width]
        Y = R * np.sin(Theta) + depth / 2    # shift Y to [0, depth]

        ax.plot_surface(X, Y, Z, color='gray', edgecolor='none', linewidth=0, alpha=1.0)

        # Draw top face
        top_circle_x = r_top * np.cos(theta) + width / 2
        top_circle_y = r_top * np.sin(theta) + depth / 2
        top_circle_z = np.full_like(top_circle_x, height)
        ax.add_collection3d(Poly3DCollection([list(zip(top_circle_x, top_circle_y, top_circle_z))],
                                             facecolor='gray', edgecolor='black', alpha=1.0))

        center_top = (width / 2, depth / 2, height)

    elif base_type == "spherical":
        radius = width / 2
        u = np.linspace(np.pi / 2, np.pi, 30)
        v = np.linspace(0, 2 * np.pi, 30)
        U, V = np.meshgrid(u, v)

        X = radius * np.sin(U) * np.cos(V) + width / 2
        Y = radius * np.sin(U) * np.sin(V) + depth / 2
        Z = radius * np.cos(U)

        ax.plot_surface(X, Y, Z, color='gray', edgecolor='none', alpha=1.0)

        bottom_circle_x = radius * np.cos(v) + width / 2
        bottom_circle_y = radius * np.sin(v) + depth / 2
        bottom_circle_z = np.full_like(bottom_circle_x, 0.0)
        ax.add_collection3d(Poly3DCollection([list(zip(bottom_circle_x, bottom_circle_y, bottom_circle_z))],
                                             facecolor='gray', edgecolor='black', alpha=1.0))

        center_top = (width / 2, depth / 2)

    ax.set_box_aspect([width, depth, height])
    ax.view_init(elev=15, azim=0)
    ax.set_axis_off()
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, transparent=True)
    plt.close()
    print(f"Base saved to: {filename}")
    return center_top




def draw_flat_base(filename, base_type, add_feet):
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.set_aspect('equal')
    ax.axis('off')

    width = random.uniform(6, 8)
    height = random.uniform(2, 3)
    top_depth = random.uniform(0.3, 0.5)
    top_shrink = random.uniform(0.7, 0.9)
    corner_radius = min(0.6, height * 0.25)

    # Base front face vertices
    if base_type in ["trapezoidal", "curved trapezoidal"]:
        shrink = random.uniform(0.7, 0.9)
        top_right = (width * shrink + (1 - shrink) * width / 2, height)
        top_left = ((1 - shrink) * width / 2, height)
    else:
        top_left = (0, height)
        top_right = (width, height)

    bottom_left = (0, 0)
    bottom_right = (width, 0)

    def arc(cx, cy, start_angle, end_angle, r, steps=6):
        angles = np.linspace(start_angle, end_angle, steps)
        return [(cx + r * np.cos(a), cy + r * np.sin(a)) for a in angles]

    def vertical_curve(p1, p2, amount=0.2, steps=10):
        xs = np.linspace(p1[0], p2[0], steps)
        ys = np.linspace(p1[1], p2[1], steps)
        dx = amount * np.sin(np.linspace(0, np.pi, steps))
        return list(zip(xs + dx, ys))

    #FRONT FACE
    if base_type == "curved trapezoidal":
        front_face = []
        front_face += arc(bottom_left[0] + corner_radius, bottom_left[1] + corner_radius,
                          np.pi, 1.5 * np.pi, corner_radius)
        front_face.append((bottom_right[0] - corner_radius, bottom_right[1]))
        front_face += arc(bottom_right[0] - corner_radius, bottom_right[1] + corner_radius,
                          1.5 * np.pi, 2 * np.pi, corner_radius)

        left_curve = vertical_curve((bottom_left[0], bottom_left[1] + corner_radius), top_left, amount=0.2)
        right_curve = vertical_curve((bottom_right[0], bottom_right[1] + corner_radius), top_right, amount=-0.2)

        front_face += right_curve
        front_face += left_curve[::-1]
    else:
        front_face = []
        front_face += arc(bottom_left[0] + corner_radius, bottom_left[1] + corner_radius,
                          np.pi, 1.5 * np.pi, corner_radius)
        front_face.append((bottom_right[0] - corner_radius, bottom_right[1]))
        front_face += arc(bottom_right[0] - corner_radius, bottom_right[1] + corner_radius,
                          1.5 * np.pi, 2 * np.pi, corner_radius)
        front_face.append((top_right[0], top_right[1] - corner_radius))
        front_face += arc(top_right[0] - corner_radius, top_right[1] - corner_radius, 0, 0.5 * np.pi, corner_radius)
        front_face.append((top_left[0] + corner_radius, top_left[1]))
        front_face += arc(top_left[0] + corner_radius, top_left[1] - corner_radius,
                          0.5 * np.pi, np.pi, corner_radius)
        front_face.append((bottom_left[0], bottom_left[1] + corner_radius))

    ax.add_patch(patches.Polygon(front_face, closed=True, facecolor="gray", edgecolor="black", linewidth=2))

    # TOP FACE
    if base_type == "curved trapezoidal":
        top_left_corner = left_curve[-1]
        top_right_corner = right_curve[-1]
    else:
        top_left_corner = (top_left[0] + corner_radius / 1.5, top_left[1])
        top_right_corner = (top_right[0] - corner_radius / 1.5, top_right[1])

    top_inner_left = (
        top_left_corner[0] + (top_right_corner[0] - top_left_corner[0]) * (1 - top_shrink) / 2,
        top_left_corner[1] + top_depth
    )
    top_inner_right = (
        top_right_corner[0] - (top_right_corner[0] - top_left_corner[0]) * (1 - top_shrink) / 2,
        top_right_corner[1] + top_depth
    )

    if base_type == "curved trapezoidal":
        top_face = []
        top_face.append(top_left_corner)
        top_face.append(top_right_corner)
        top_face.append(top_inner_right)
        top_face.append(top_inner_left)
    else:
        top_face = [
            top_left_corner,
            top_right_corner,
            top_inner_right,
            top_inner_left
        ]

    ax.add_patch(patches.Polygon(top_face, closed=True, facecolor="#cccccc", edgecolor="black", linewidth=2))

    if add_feet:
        foot_width = width * 0.15
        foot_height = 0.2
        spacing = width * 0.25
        base_y = 0 

        for x_offset in [-spacing, spacing]:
            rect = patches.Rectangle(
                (width / 2 + x_offset - foot_width / 2, base_y - foot_height),
                foot_width, foot_height,
                linewidth=0, facecolor='grey'
            )
            ax.add_patch(rect)
        

        top_center_x = (top_left_corner[0] + top_right_corner[0]) / 2
        top_center_y = (top_left_corner[1] + top_inner_left[1]) / 2

    ax.set_xlim(-1, width + 2)
    ax.set_ylim(-1, height + top_depth + 1)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, transparent=True)
    plt.close()
    print(f"Flat base saved to: {filename}")
    return (top_center_x, top_center_y)


