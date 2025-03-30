import math
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from noise import pnoise2
from math import pi as PI

def norm_rand(min_val, max_val):
    return random.uniform(min_val, max_val)

def mapval(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def rand_choice(options):
    return random.choice(options)

def sigmoid(x, coeff):
    return 1 / (1 + math.exp(-x * coeff))

def noise(x, seed):
    return pnoise2(x, seed)

def gen_params(flower_color="#ff69b4", alpha=0.7):
    PAR = {}

    randint = lambda x, y: math.floor(norm_rand(x, y))
    pow = math.pow
    sin = math.sin

    def flower_shape_mask(x):
        return math.pow(math.sin(PI * x), 0.2)

    PAR['flowerChance'] = rand_choice([norm_rand(0, 0.08), norm_rand(0, 0.03)])
    PAR['flowerLength'] = norm_rand(5, 55)
    PAR['flowerWidth'] = norm_rand(5, 30)

    flower_shape_noise_seed = random.random() * PI
    flower_jaggedness = norm_rand(8, 15)

    def flower_shape(x):
        return noise(x * flower_jaggedness, flower_shape_noise_seed) * flower_shape_mask(x)

    PAR['flowerShape'] = flower_shape
    PAR['flowerColor'] = {
        'rgb': mcolors.to_rgb(flower_color),
        'alpha': alpha
    }

    curve_coeff0 = [norm_rand(-0.5, 0.5), norm_rand(5, 10)]
    curve_coeff2 = [random.random() * PI, norm_rand(5, 15)]
    curve_coeff4 = [random.random() * 0.5, norm_rand(0.8, 1.2)]

    def flower_open_curve_1(x, op):
        if x < 0.1:
            return 2 + op * curve_coeff2[1]
        else:
            return noise(x * 10, curve_coeff2[0])

    def flower_open_curve_2(x, op):
        if x < curve_coeff4[0]:
            return 0
        else:
            return 10 - x * mapval(op, 0, 1, 16, 20) * curve_coeff4[1]

    PAR['flowerOpenCurve'] = rand_choice([flower_open_curve_1, flower_open_curve_2])
    PAR['flowerColorCurve'] = lambda x: sigmoid(x + curve_coeff0[0], curve_coeff0[1])
    PAR['flowerPetal'] = round(mapval(PAR['flowerWidth'], 5, 50, 10, 3))

    return PAR

def draw_flower(PAR, filename="flower.png"):
    shape_func = PAR['flowerShape']
    petal_count = PAR['flowerPetal']

    angles = np.linspace(0, 2 * np.pi, 100)
    fig, ax = plt.subplots(figsize=(5, 5))

    for i in range(petal_count):
        offset = 2 * np.pi * i / petal_count
        r = np.array([shape_func(x) for x in np.linspace(0, 1, 100)])
        r = r / np.max(r)  
        r = 1 + 0.6 * r 
        theta = angles + offset
        x = r * np.cos(theta)
        y = r * np.sin(theta)

        rgb = PAR['flowerColor']['rgb']
        alpha = PAR['flowerColor']['alpha']
        ax.fill(x, y, color=rgb, alpha=alpha)

    ax.set_aspect('equal')
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"Saved flower image to: {filename}")

def draw_flower_at(ax, x, y, angle, PAR, scale=1.0):
    shape_func = PAR['flowerShape']
    petal_count = PAR['flowerPetal']
    angles = np.linspace(0, 2 * np.pi, 100)

    for i in range(petal_count):
        offset = 2 * np.pi * i / petal_count
        r = np.array([shape_func(xi) for xi in np.linspace(0, 1, 100)])
        r = r / np.max(r)
        r = 1 + 0.6 * r
        theta = angles + offset
        x_pts = r * np.cos(theta) * scale
        y_pts = r * np.sin(theta) * scale

        # rotate and shift
        x_rot = x_pts * np.cos(np.radians(angle)) - y_pts * np.sin(np.radians(angle))
        y_rot = x_pts * np.sin(np.radians(angle)) + y_pts * np.cos(np.radians(angle))

        rgb = PAR['flowerColor']['rgb']
        alpha = PAR['flowerColor']['alpha']
        ax.fill(x + x_rot, y + y_rot, color=rgb, alpha=alpha)
