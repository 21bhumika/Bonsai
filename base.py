import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import random

def draw_base(ax, center=None, color=None):
    base_type = random.choice(["cuboid", "trapezoidal", "cylinder", "curved trapezoidal", "spherical"])
    print(f"Base type selected: {base_type}")
    
    add_feet = random.random() < 0.5
    # if base_type in ["cylinder", "spherical"]:
    #     draw_3D_base(ax, base_type, center, color)
    # else:
    draw_flat_base(ax, base_type, add_feet, center, color)

def draw_3D_base(ax, base_type, center=None, color=None):
    height = random.uniform(0.5, 2.0)
    width = random.uniform(4.0, 8.0)
    depth = random.uniform(2.0, 4.0)

    if base_type == "cylinder":
        r_top = random.uniform(0.5, 1.0) * (width / 2)
        r_bot = width / 2
        z = np.linspace(0, height, 100)
        theta = np.linspace(0, 2 * np.pi, 200)
        Z, Theta = np.meshgrid(z, theta)

        R = np.linspace(r_bot, r_top, len(z))
        R = np.tile(R, (len(theta), 1))
        X = R * np.cos(Theta) + width / 2
        Y = R * np.sin(Theta) + depth / 2

        ax.plot_surface(
            X, Y, Z,
            color=color,
            edgecolor='none',
            linewidth=0,
            rstride=1,
            cstride=1,
            antialiased=False,
            shade=False
        )

        # Top face
        top_circle_x = r_top * np.cos(theta) + width / 2
        top_circle_y = r_top * np.sin(theta) + depth / 2
        top_circle_z = np.full_like(top_circle_x, height - 0.01)
        ax.add_collection3d(Poly3DCollection([list(zip(top_circle_x, top_circle_y, top_circle_z))],
                                             facecolor=color, edgecolor='none', alpha=1.0))

        if center is not None:
            center["x"] = width / 2
            center["y"] = depth / 2

    elif base_type == "spherical":
        radius = width / 2
        u = np.linspace(np.pi / 2, np.pi, 100)
        v = np.linspace(0, 2 * np.pi, 200)
        U, V = np.meshgrid(u, v)

        X = radius * np.sin(U) * np.cos(V) + width / 2
        Y = radius * np.sin(U) * np.sin(V) + depth / 2
        Z = radius * np.cos(U)

        ax.plot_surface(
            X, Y, Z,
            color=color,
            edgecolor='none',
            linewidth=0,
            rstride=1,
            cstride=1,
            antialiased=False,
            shade=False
        )

        bottom_circle_x = radius * np.cos(v) + width / 2
        bottom_circle_y = radius * np.sin(v) + depth / 2
        bottom_circle_z = np.full_like(bottom_circle_x, 0.0)
        ax.add_collection3d(Poly3DCollection([list(zip(bottom_circle_x, bottom_circle_y, bottom_circle_z))],
                                             facecolor=color, edgecolor='none', alpha=1.0))

        if center is not None:
            center["x"] = width / 2
            center["y"] = depth / 2

    ax.set_box_aspect([width, depth, height])
    ax.view_init(elev=15, azim=0)
    ax.set_axis_off()
    # fig.patch.set_alpha(0.0)
    # ax.patch.set_alpha(0.0)
    # plt.tight_layout()
    # plt.savefig(filename, dpi=300, transparent=True)
    # plt.close()
    # print(f"Base saved to: {filename}")

def draw_flat_base(ax, base_type, add_feet, center=None, color=None):
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

    ax.add_patch(patches.Polygon(front_face, closed=True, facecolor=color, edgecolor="none", linewidth=2))

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

    top_face = [top_left_corner, top_right_corner, top_inner_right, top_inner_left]
    ax.add_patch(patches.Polygon(top_face, closed=True, facecolor=color, edgecolor="none", linewidth=2))

    # Compute top center
    top_center_x = (top_left_corner[0] + top_right_corner[0]) / 2
    top_center_y = (top_left_corner[1] + top_inner_left[1]) / 2

    if center is not None:
        center["x"] = top_center_x
        center["y"] = top_center_y

    # Draw feet if needed
    if add_feet:
        foot_width = width * 0.15
        foot_height = 0.2
        spacing = width * 0.25
        base_y = 0 

        for x_offset in [-spacing, spacing]:
            rect = patches.Rectangle(
                (width / 2 + x_offset - foot_width / 2, base_y - foot_height),
                foot_width, foot_height,
                linewidth=0, facecolor=color
            )
            ax.add_patch(rect)

    ax.set_xlim(-1, width + 2)
    ax.set_ylim(-1, height + top_depth + 1)
    # plt.tight_layout()
    # plt.savefig(filename, dpi=300, transparent=True)
    # plt.close()
    # print(f"Flat base saved to: {filename}")
