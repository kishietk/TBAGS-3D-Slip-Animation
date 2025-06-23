# cores/sandbagUnit.py

"""
ファイル名: cores/sandbagUnit.py

責務:
    - 2つのサンドバッグノードから1つのSandbagUnitを構成
    - ノードのグループ化、ユニットID生成、重心計算、座標アクセスを提供
    - ペアリングロジックを含むユーティリティ関数pair_sandbag_nodes
"""

from typing import List, Dict, Tuple
from mathutils import Vector
from configs.kind_labels import SANDBAG_NODE_KIND_IDS
from cores.nodeCore import Node


class SandbagUnit:
    """
    2ノードで構成されるサンドバッグユニット。

    Attributes:
        nodes (List[Node]): ユニットを構成する2つのノード
        id (str): 一意ID（"nodeA_nodeB"）
        centroid (Vector): 2点の中点
        z_values (List[float]): 各ノードのZ座標リスト
    """

    def __init__(self, nodes: List[Node]):
        assert len(nodes) == 2, "SandbagUnit requires exactly 2 nodes"
        # Z座標順にソートし、重心とIDを生成
        sorted_nodes = sorted(nodes, key=lambda n: n.pos.z)
        self.nodes: List[Node] = sorted_nodes
        self.id: str = f"{sorted_nodes[0].id}_{sorted_nodes[1].id}"
        # 中点計算
        pos_sum = sorted_nodes[0].pos + sorted_nodes[1].pos
        self.centroid: Vector = pos_sum / 2
        # Z座標リスト
        self.z_values: List[float] = [n.pos.z for n in sorted_nodes]

    def __repr__(self) -> str:
        node_ids = [n.id for n in self.nodes]
        return f"SandbagUnit(id={self.id}, nodes={node_ids}, centroid={tuple(self.centroid)})"


# TODO:
# - Nodeクラスとの依存を減らすため、posプロパティの抽象化を検討
# - 単体テストの導入: 異常系（奇数ノード、kind_id外）に対する挙動確認
# - 座標丸め精度(rnd)とグルーピングキーのパラメータ化


def pair_sandbag_nodes(nodes: Dict[int, Node]) -> List[SandbagUnit]:
    """
    サンドバッグノードを(X,Y)でグループ化し、高さ順に2つずつペアにしてユニット生成。

    Args:
        nodes: 全ノードID->Nodeマップ
    Returns:
        List[SandbagUnit]: ペアリングされたサンドバッグユニットのリスト

    Note:
        - X,Y座標は小数第4位で丸め処理
        - 余りのノードは無視される
    """
    from collections import defaultdict

    xy_groups: Dict[Tuple[float, float], List[Node]] = defaultdict(list)
    # サンドバッグノードのみ抽出
    for node in nodes.values():
        if node.kind_id in SANDBAG_NODE_KIND_IDS:
            key = (round(node.pos.x, 4), round(node.pos.y, 4))
            xy_groups[key].append(node)

    units: List[SandbagUnit] = []
    for group in xy_groups.values():
        # Z座標でソート
        group.sort(key=lambda n: n.pos.z)
        # 2ノードずつペアリング
        for i in range(0, len(group) - 1, 2):
            pair = group[i : i + 2]
            if len(pair) == 2:
                units.append(SandbagUnit(pair))
    return units
