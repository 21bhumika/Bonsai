import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
from matplotlib.patches import PathPatch

def draw_plant_pot(ax, root_x, root_y, pot_width=140, pot_height=30, pot_color=None):
    top_width = pot_width
    draw_rounded_trapezoid(ax, root_x, root_y - 30, top_width=100, bottom_width=140, height=30, radius=10, color=pot_color)

    soil = patches.Arc((root_x, root_y), top_width * 0.75, 25   , theta1=0, theta2=180, color=pot_color, lw=3)
    ax.add_patch(soil)

def draw_rounded_trapezoid(ax, root_x, root_y, top_width=140, bottom_width=100, height=30, radius=10, color='peru'):
    half_top = top_width / 2
    half_bottom = bottom_width / 2

    top_left = (root_x - half_top, root_y)
    top_right = (root_x + half_top, root_y)
    bottom_right = (root_x + half_bottom, root_y + height)
    bottom_left = (root_x - half_bottom, root_y + height)

    ctrl_offset_x = (half_top - half_bottom) * 0.8
    ctrl_offset_y = height * 0.5

    verts = [
        top_left,                                                    
        top_right,                                                  
        (top_right[0] - ctrl_offset_x, top_right[1] + ctrl_offset_y),  
        bottom_right,                
        bottom_left,
        (top_left[0] + ctrl_offset_x, top_left[1] + ctrl_offset_y),
        top_left
    ]

    codes = [
        Path.MOVETO,     # top_left
        Path.LINETO,     # top_right
        Path.CURVE3,     # right
        Path.CURVE3,     # bottom_right
        Path.LINETO,     # bottom_left
        Path.CURVE3,     # left
        Path.CURVE3      # back
    ]

    path = Path(verts, codes)
    patch = PathPatch(path, facecolor=color, edgecolor='none')
    ax.add_patch(patch)