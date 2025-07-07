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
        nodes: [高いノード, 低いノード] の順で受け取る Node リスト（長さ 2）
        id: "{低いノードID}_{高いノードID}"
        centroid: 2点の重心ベクトル
        z_values: [高いノードの z, 低いノードの z]
    """

    nodes: List[Node]
    id: str = field(init=False)
    centroid: Vector = field(init=False)
    z_values: List[float] = field(init=False)

    def __post_init__(self):
        # ノード数チェック
        assert len(self.nodes) == 2, "Sandbag requires exactly 2 nodes"
        # 受け取る順番を [高い, 低い] として扱う
        high, low = self.nodes

        # ID 生成
        self.id = f"{high.id}_{low.id}"

        # 重心計算
        self.centroid = low.pos

        # z値リスト (high_z, low_z)
        self.z_values = [high.pos.z, low.pos.z]
