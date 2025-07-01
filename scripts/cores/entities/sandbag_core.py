# cores/entities/sandbag_core.py

from dataclasses import dataclass, field
from typing import List
from .node_core import Node
from mathutils import Vector


@dataclass
class Sandbag:
    """
    2ノードで構成されるサンドバッグユニットのデータモデル。
    Attributes:
        nodes: z座標でソート済みの Node リスト（長さ 2）
        id: "{低いノードID}_{高いノードID}"
        centroid: 2点の重心ベクトル
        z_values: [低いノードの z, 高いノードの z]
    """

    nodes: List[Node]
    id: str = field(init=False)
    centroid: Vector = field(init=False)
    z_values: List[float] = field(init=False)

    def __post_init__(self):
        # ノード数チェック＆ソート
        assert len(self.nodes) == 2, "Sandbag requires exactly 2 nodes"
        self.nodes.sort(key=lambda n: n.pos.z)

        # ID 生成
        low, high = self.nodes
        self.id = f"{low.id}_{high.id}"

        # 重心計算
        self.centroid = (low.pos + high.pos) / 2

        # z値リスト
        self.z_values = [low.pos.z, high.pos.z]
