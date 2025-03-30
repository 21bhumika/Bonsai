import json
import numpy as np

def export_tree_to_json(filename, trunk_segments, buds, branch_trees=None, leaves=None):
    def serialize_branch(node):
        return {
            "points": node["points"],
            "children": [serialize_branch(child) for child in node["children"]]
        }

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
    if branch_trees is not None:
        data["branches"] = [serialize_branch(tree) for tree in branch_trees]

    if leaves is not None:
        data["leaves"] = [
            {"pos": [float(x), float(y)]} for x, y in leaves
        ]

    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Tree structure exported to {filename}")

# === JSON 读取工具 ===
def import_tree_from_json(filename):
    def deserialize_branch(data):
        return {
            "points": data["points"],
            "children": [deserialize_branch(child) for child in data.get("children", [])]
        }

    with open(filename, 'r') as f:
        data = json.load(f)

    trunk_segments = [
        (np.array([pt[0] for pt in seg["points"]]), np.array([pt[1] for pt in seg["points"]]))
        for seg in data["trunk"]
    ]
    buds = data.get("buds", [])
    leaves = [(leaf["pos"][0], leaf["pos"][1]) for leaf in data.get("leaves", [])]
    branch_trees = [deserialize_branch(tree) for tree in data.get("branches", [])]

    return trunk_segments, buds, branch_trees, leaves