"""
ファイル名: configs/node_ids.py

責務:
- ノードIDやグループを一元管理
"""

# ----------------------------
# ノードID・グループ定義
# ----------------------------
NODE_IDS_3STORY = (
    {1143, 1148, 1153, 1158, 1243, 1248, 1253, 1258}
    | set(range(201, 209))
    | set(range(301, 309))
    | set(range(401, 409))
)

NODE_IDS_NOKOTSUDO = (
    set(range(201, 309))
    | set(range(401, 509))
    | set(range(601, 709))
    | set(range(1101, 1313))
)

VALID_NODE_IDS = NODE_IDS_3STORY
