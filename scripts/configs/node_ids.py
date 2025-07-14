"""
ファイル名: configs/node_ids.py

責務:
- ノードIDやグループを一元管理
"""

# ----------------------------
# ノードID・グループ定義
# ----------------------------
NODE_IDS_1F = {1143, 1148, 1153, 1158, 1243, 1248, 1253, 1258}
NODE_IDS_2F = set(range(201, 209))
NODE_IDS_3F = set(range(301, 309))
NODE_IDS_4F = set(range(401, 409))


VALID_NODE_IDS = set().union(NODE_IDS_1F, NODE_IDS_2F, NODE_IDS_3F, NODE_IDS_4F)
