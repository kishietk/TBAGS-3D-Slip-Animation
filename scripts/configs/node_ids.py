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

VALID_NODE_IDS = set().union(
    NODE_IDS_2F,
    NODE_IDS_3F,
    NODE_IDS_4F
)
