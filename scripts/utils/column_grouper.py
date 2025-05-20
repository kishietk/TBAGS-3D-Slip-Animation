# utils/column_grouper.py

from collections import defaultdict, deque
from typing import List, Tuple
from utils.logging import setup_logging  # ← ここで共通ロギング

log = setup_logging()

"""
column_grouper.py

【責任】
- kind_id=53等でフィルタされた「柱エッジリスト（ノードIDペア）」から
  “連結したノード系列ごと”に「柱グループ（ノードIDリスト）」を自動抽出。

【使い方】
- parapet_edges = [(1143,201), (201,301), (301,401), ...]
- groups = group_columns_by_edges(parapet_edges)
→ groups == [[1143,201,301,401], [1148,202,302,402], ...]（例：8本）

"""


def group_columns_by_edges(edges: List[Tuple[int, int]]) -> List[List[int]]:
    """
    与えられたエッジリストから「連結した柱グループ（ノードIDリスト）」を抽出

    引数:
        edges: [(a, b), ...]（例: [(1143,201), (201,301), ...]）

    戻り値:
        groups: [[n1, n2, ...], ...]（1柱ごとノードIDリスト、例:8本）
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
        # BFSでこの柱グループの全ノードを探索
        q = deque([n])
        group = []
        while q:
            curr = q.popleft()
            if curr in visited:
                continue
            visited.add(curr)
            group.append(curr)
            for nbr in connect[curr]:
                if nbr not in visited:
                    q.append(nbr)
        # 2つ以上でグループ化
        if len(group) > 1:
            log.info(f"Column group found: {group}")
            groups.append(group)
    log.info(f"Column grouping complete: {len(groups)} groups")
    return groups