def collect_leaf_positions(buds, branch_trees, crown_ratio=0.85):
    leaf_positions = []

    # 来自 bud 的花朵
    for bud in buds:
        if bud['fate'] == 'flower':
            leaf_positions.append(bud['pos'])

    # 递归收集 branch_tree 的末端
    def dfs(node):
        pts = node["points"]
        if not node["children"]:
            leaf_positions.append(tuple(pts[-1]))  # 终点
        for child in node["children"]:
            dfs(child)

    for tree in branch_trees:
        dfs(tree)

    return leaf_positions
