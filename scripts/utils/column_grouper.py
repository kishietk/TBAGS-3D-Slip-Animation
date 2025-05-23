# utils/column_grouper.py

from collections import defaultdict, deque
from typing import List, Tuple
from utils.logging import setup_logging  # ← 共通ロギング

log = setup_logging()

"""
column_grouper.py

【責任】
- kind_id=53等でフィルタされた「柱エッジリスト（ノードIDペア）」から
  “連結したノード系列ごと”に「柱グループ（ノードIDリスト）」を自動抽出。

【使い方】
- pillar_edges = [(1143,201), (201,301), (301,401), ...]
- groups = group_columns_by_edges(pillar_edges)
→ groups == [[1143,201,301,401], [1148,202,302,402], ...]（例：8本）

"""


def group_columns_by_edges(edges: List[Tuple[int, int]]) -> List[List[int]]:
    """
    与えられたエッジリストから「連結した柱グループ（端点→端点の順列）」を抽出

    引数:
        edges: [(a, b), ...]（例: [(1143,201), (201,301), ...]）

    戻り値:
        groups: [[n1, n2, ...], ...]（1柱ごとノードIDリスト、端点順）
    """
    log.info(f"Start grouping columns: {len(edges)} edges")
    connect = defaultdict(list)
    for a, b in edges:
        connect[a].append(b)
        connect[b].append(a)

    groups = []
    visited = set()

    for n in connect:
        if n in visited:
            continue
        # 端点探索（次数1のノード）
        degree1 = [k for k in connect if len(connect[k]) == 1 and k not in visited]
        if not degree1:
            # ループ状も念のため対応: 適当にスタート
            start = n
        else:
            start = degree1[0]
        # 端点→端点まで一直線にたどる
        seq = []
        curr = start
        prev = None
        while True:
            seq.append(curr)
            visited.add(curr)
            nbrs = [nb for nb in connect[curr] if nb != prev]
            if not nbrs:
                break
            prev, curr = curr, nbrs[0]
        if len(seq) > 1:
            log.info(f"Column group (ordered): {seq}")
            groups.append(seq)
    log.info(f"Column grouping complete: {len(groups)} groups")
    return groups
