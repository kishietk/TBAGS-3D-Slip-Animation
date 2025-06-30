# builders/object_builders/beam_builder.py

"""
ファイル名: builders/object_builders/beam_builder.py

責務:
- コアモデルのエッジ情報（梁用エッジ）から Blender 円柱（梁）を生成し、シーンに配置する。
- thickness パラメータで梁の直径（太さ）を制御する。
- 生成失敗時はログに記録し、処理を継続。

TODO:
- キャップ付き / 開口付き梁のオプション追加
- 回転ロジック共通化（ColumnBuilder と重複しているため）
"""

import bpy
from mathutils import Vector, Matrix
from typing import Dict, Set, Tuple
from utils import setup_logging
from builders.base import BuilderBase

log = setup_logging("BeamBuilder")


class BeamBuilder(BuilderBase):
    def __init__(
        self,
        positions: Dict[int, Vector],
        edges: Set[Tuple[int, int]],
        thickness: float = 0.1,
        name_prefix: str = "Beam",
    ):
        """
        初期化:
            positions: ノードID→座標 Vector の辞書
            edges:      (start_id, end_id) の集合
            thickness:  円柱の直径（Blender 単位）
            name_prefix: 作成オブジェクト名のプレフィクス
        """
        super().__init__()
        self.positions = positions
        self.edges = edges
        self.thickness = thickness
        self.name_prefix = name_prefix

    def build(self) -> Dict[str, bpy.types.Object]:
        """
        役割:
            各エッジをつなぐ円柱を生成し、
            “start_end” 形式のキーで辞書に格納して返却。

        返り値:
            Dict[str, bpy.types.Object]: キー"{start}_{end}"→生成された Blender オブジェクト
        """
        objs: Dict[str, bpy.types.Object] = {}
        for start, end in self.edges:
            try:
                p0 = self.positions[start]
                p1 = self.positions[end]
            except KeyError as e:
                log.error(
                    f"BeamBuilder: ノード {e.args[0]} が positions に見つかりません。スキップします。"
                )
                continue

            # 中点と方向、長さを計算
            delta = p1 - p0
            length = delta.length
            mid = p0 + delta * 0.5

            # 回転行列を作成（Z軸→delta方向）
            up = Vector((0, 0, 1))
            axis = up.cross(delta)
            if axis.length < 1e-6:
                rot_mat = Matrix.Identity(3)
            else:
                angle = up.angle(delta)
                rot_mat = Matrix.Rotation(angle, 4, axis.normalized())

            # 円柱を追加
            bpy.ops.mesh.primitive_cylinder_add(
                radius=self.thickness / 2,
                depth=length,
                location=mid,
            )
            obj = bpy.context.object
            obj.name = f"{self.name_prefix}_{start}_{end}"

            # 回転適用
            obj.matrix_world @= rot_mat.to_4x4()

            key = f"{start}_{end}"
            objs[key] = obj
            log.debug(
                f"{obj.name} created between {start} and {end}, thickness={self.thickness}, length={length:.3f}"
            )

        log.info(f"{len(objs)} 件の梁オブジェクトを生成しました。")
        return objs
