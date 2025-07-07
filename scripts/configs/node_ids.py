"""
ファイル名: configs/node_ids.py

責務:
- ノードIDやグループを一元管理
"""


# ----------------------------
# ノードID・グループ定義
# ----------------------------
NODE_IDS_2F = set(range(201, 209))
NODE_IDS_3F = set(range(301, 309))
NODE_IDS_4F = set(range(401, 409))


# ----------------------------
# 代表サンドバックを構成するノードID
# ----------------------------
SANDBAG_NODE_IDS_KIND_1 = {1143, 1148, 1153, 1158, 1243, 1248, 1253, 1258}
SANDBAG_NODE_IDS_KIND_2 = {3143, 3148, 3153, 3158, 3243, 3248, 3253, 3258}
SANDBAG_NODE_IDS_KIND_3 = {5143, 5148, 5153, 5158, 5243, 5248, 5253, 5258}
SANDBAG_NODE_IDS_KIND_4 = {11143, 11148, 11153, 11158, 11243, 11248, 11253, 11258}
# SANDBAG_NODE_IDS_KIND_5 = {2354, 2359, 2366, 2372, 2379, 2385, 2391}
# SANDBAG_NODE_IDS_KIND_6 = {4354, 4359, 4366, 4372, 4379, 4385, 4391}
# SANDBAG_NODE_IDS_KIND_7 = {6354, 6359, 6366, 6372, 6379, 6385, 6391}
# SANDBAG_NODE_IDS_KIND_8 = {12354, 12359, 12366, 12372, 12379, 12385, 12391}

SANDBAG_NODE_IDS = {
    1: SANDBAG_NODE_IDS_KIND_1,
    2: SANDBAG_NODE_IDS_KIND_2,
    3: SANDBAG_NODE_IDS_KIND_3,
    4: SANDBAG_NODE_IDS_KIND_4,
    # 5: SANDBAG_NODE_IDS_KIND_5,
    # 6: SANDBAG_NODE_IDS_KIND_6,
    # 7: SANDBAG_NODE_IDS_KIND_7,
    # 8: SANDBAG_NODE_IDS_KIND_8,
}

VALID_NODE_IDS = set().union(
    NODE_IDS_2F, NODE_IDS_3F, NODE_IDS_4F, *SANDBAG_NODE_IDS.values()
)

# ----------------------------
# 複製サンドバックの座標取得のための、ノードID定義
# ----------------------------
