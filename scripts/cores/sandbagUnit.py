"""
ファイル名: cores/sandbagUnit.py

責務:
- 2つのサンドバッグノード（kind_idで区別）から1つのSandbagUnitオブジェクトを構成。
- サンドバッグノードのグルーピング・一意ID・重心計算・属性アクセスを一元管理。
- サンドバッグのペアリング（ノード2つ→ユニット化）ロジックもここで提供。

設計方針:
- kind_idでサンドバッグノードを抽出し、(x, y)が等しい2つのノードをZ昇順でセット化。
- 一意IDはノードID連結。
- 必要に応じて重心座標やZ最大・最小値なども計算。
"""

from typing import List, Dict
from mathutils import Vector
from configs.kind_labels import SANDBAG_NODE_KIND_IDS
from cores.nodeCore import Node


class SandbagUnit:
    """
    役割:
        2つのsandbagノードで構成されるサンドバッグユニット。
    属性:
        nodes (List[Node]): 2つのサンドバッグノード
        id (str): 一意ID（ノードID連結）
        centroid (Vector): 2点の中点
        z_values (List[float]): Z座標リスト
    """

    def __init__(self, nodes: List):
        assert len(nodes) == 2, "SandbagUnitは2ノード必要"
        self.nodes = sorted(nodes, key=lambda n: n.pos.z)
        self.id = "_".join(str(n.id) for n in self.nodes)
        self.centroid = sum((n.pos for n in self.nodes), Vector()) / 2
        self.z_values = [n.pos.z for n in self.nodes]

    def __repr__(self):
        ids = [n.id for n in self.nodes]
        return (
            f"SandbagUnit(id={self.id}, nodes={ids}, centroid={tuple(self.centroid)})"
        )


def pair_sandbag_nodes(nodes: Dict[int, "Node"]) -> List[SandbagUnit]:
    """
    役割:
        kind_idでサンドバッグノードを抽出し、(x, y)が等しいものを高さZ順で2つペアリングしてSandbagUnitを作成。
    引数:
        nodes: 全ノード辞書
    返り値:
        List[SandbagUnit]: サンドバッグユニットのリスト
    """
    from collections import defaultdict

    xy_groups = defaultdict(list)
    for n in nodes.values():
        if getattr(n, "kind_id", None) in SANDBAG_NODE_KIND_IDS:
            # 座標の微小誤差を吸収して(X,Y)一致グループ化
            key = (round(n.pos.x, 4), round(n.pos.y, 4))
            xy_groups[key].append(n)

    sandbag_units = []
    for group in xy_groups.values():
        group.sort(key=lambda n: n.pos.z)
        # 2つずつペアにする
        for i in range(0, len(group) - 1, 2):
            pair = group[i : i + 2]
            if len(pair) == 2:
                sandbag_units.append(SandbagUnit(pair))
            # 余り1ノードは無視または警告可
    return sandbag_units
