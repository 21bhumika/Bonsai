import json
import numpy as np

def export_tree_to_json(filename, trunk_segments, buds, branch_segments=None, branch_leaves=None):
    data = {
        "trunk": [
            {"points": [[float(x), float(y)] for x, y in zip(xs, ys)]}
            for xs, ys in trunk_segments
        ],
        "buds": [
            {"pos": [float(b['pos'][0]), float(b['pos'][1])], "angle": float(b['angle']), "fate": b['fate']}
            for b in buds
        ]
    }
    if branch_segments is not None:
        data["branches"] = [
            {"segments": [[float(x0), float(y0)], [float(x1), float(y1)]]}
            for (x0, y0), (x1, y1) in branch_segments
        ]
    if branch_leaves is not None:
        data["branch_leaves"] = [
            {"pos": [float(x), float(y)]} for x, y in branch_leaves
        ]

    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Tree structure exported to {filename}")

def import_tree_from_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)

    trunk_segments = [
        (np.array([p[0] for p in trunk["points"]]), np.array([p[1] for p in trunk["points"]]))
        for trunk in data.get("trunk", [])
    ]

    buds = [
        {
            "pos": tuple(bud["pos"]),
            "angle": bud["angle"],
            "fate": bud["fate"]
        }
        for bud in data.get("buds", [])
    ]

    branches = [
        (tuple(seg["segments"][0]), tuple(seg["segments"][1]))
        for seg in data.get("branches", [])
    ] if "branches" in data else []

    leaves = [
        tuple(leaf["pos"])
        for leaf in data.get("leaves", [])
    ] if "leaves" in data else []

    print(f"Tree structure loaded from {filename}")
    return trunk_segments[::-1], buds[::-1], branches[::-1], leaves[::-1]
