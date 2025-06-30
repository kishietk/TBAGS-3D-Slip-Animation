"""
ファイル名: builders/object_builders/roof_builder.py

責務:
- 最上階ノード群から屋根パネル（四角形クワッド）を抽出し、Blenderオブジェクトとして生成する。
- Z最大層の格子状ノード配置にのみ対応し、それ以外の形状や異常はログに記録（例外はraiseせず復帰）。

注意点:
- ノードはID→mathutils.Vectorマッピングとして渡される。
- EPS_XY_MATCH によるXY一致判定を使用。
- Mesh.from_pydata は使用せず、頂点情報や面は外部管理（roof_quads）に委ねる。

TODO:
- 異形パネルや膨張形状対応の強化
- UV/マテリアル設定、頂点座標直接設定などの汎用化
"""

import bpy
from mathutils import Vector
from typing import Dict, Tuple, List, Optional
from utils import setup_logging
from builders.base import BuilderBase
from configs import EPS_XY_MATCH

log = setup_logging("RoofBuilder")


class RoofBuilder(BuilderBase):
    def __init__(self, nodes: Dict[int, Vector], name: str = "Roof"):
        """初期化: nodes は {node_id: Vector} 形式。"""
        super().__init__()
        self.nodes = nodes
        self.name = name

    def build(
        self,
    ) -> Tuple[Optional[bpy.types.Object], List[Tuple[int, int, int, int]]]:
        """
        役割:
            1) Z最大層ノードを抽出
            2) 格子パターンで四角形(quad)を発見
            3) Blenderオブジェクトを生成し、quadリストをプロパティに格納

        返り値:
            (RoofObject or None, List of quad tuples)
        """
        # 1) Zレベル抽出
        zs = sorted({v.z for v in self.nodes.values()})
        if not zs:
            log.warning("RoofBuilder: No Z levels found")
            return None, []
        top_z = zs[-1]
        tops: Dict[int, Vector] = {
            nid: pos
            for nid, pos in self.nodes.items()
            if abs(pos.z - top_z) < EPS_XY_MATCH
        }

        # 2) 格子状ノードをX/Yでソート
        xs = sorted({v.x for v in tops.values()})
        ys = sorted({v.y for v in tops.values()})

        def fid(x: float, y: float) -> Optional[int]:
            """座標(x,y)に最も近いノードIDを返す"""
            return next(
                (
                    nid
                    for nid, pos in tops.items()
                    if abs(pos.x - x) < EPS_XY_MATCH and abs(pos.y - y) < EPS_XY_MATCH
                ),
                None,
            )

        # クワッド探索
        quads: List[Tuple[int, int, int, int]] = []
        for i in range(len(xs) - 1):
            for j in range(len(ys) - 1):
                bl = fid(xs[i], ys[j])
                br = fid(xs[i + 1], ys[j])
                tr = fid(xs[i + 1], ys[j + 1])
                tl = fid(xs[i], ys[j + 1])
                if None not in (bl, br, tr, tl):
                    quads.append((bl, br, tr, tl))
                    log.debug(f"Roof quad: {bl}-{br}-{tr}-{tl}")

        # 3) Blenderオブジェクト生成
        try:
            mesh = bpy.data.meshes.new(f"{self.name}Mesh")
            obj = bpy.data.objects.new(self.name, mesh)
            bpy.context.collection.objects.link(obj)
            mesh.update()
            obj["roof_quads"] = quads
            log.info(f"RoofBuilder: Created {self.name} with {len(quads)} quads")
            return obj, quads
        except Exception as e:
            log.error(f"RoofBuilder: Failed to create roof object: {e}")
            return None, quads
