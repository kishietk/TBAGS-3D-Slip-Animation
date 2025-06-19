# builders/object_builders/sandbag_builder.py

"""
ファイル名: builders/object_builders/sandbag_builder.py

責務:
- コアの SandbagNode／Node オブジェクト群を受け取り、
  各位置に直方体サンドバッグを生成する。
- ノードID→Blender Object 辞書を返却し、後段のユニットビルダーやアニメーション処理と連携しやすい設計。

TODO:
- 入力型（Node／dict／tuple）統一、型ヒント強化
- 立方体サイズ・座標のバリデーション追加
- 物理シミュレーション設定との分離
"""

import bpy
from mathutils import Vector
from typing import Dict, Tuple, Any
from utils.logging_utils import setup_logging
from builders.base import BuilderBase
from cores.nodeCore import Node


class SandbagBuilder(BuilderBase):
    def __init__(
        self,
        nodes: Dict[int, Node],
        cube_size: Tuple[float, float, float],
    ):
        """
        初期化:
            nodes: ノードID→Node（または pos 属性を持つオブジェクト）マップ
            cube_size: (X, Y, Z) 各辺サイズ
        """
        super().__init__()
        self.nodes = nodes
        self.cube_size = cube_size
        self.log = setup_logging("SandbagBuilder")

    def build(self) -> Dict[int, bpy.types.Object]:
        """
        役割:
            各ノード位置に直方体サンドバッグを生成し、ノードID→Blender Object 辞書を返す。

        引数:
            なし（コンストラクタで設定済み）

        返り値:
            dict[int, bpy.types.Object]: ノードID→生成された Blender オブジェクト
        """
        objs: Dict[int, bpy.types.Object] = {}
        for nid, node in self.nodes.items():
            # pos を安全に取り出す
            if hasattr(node, "pos"):
                pos = node.pos
            elif isinstance(node, dict) and "pos" in node:
                pos = node["pos"]
            elif isinstance(node, (list, tuple)):
                pos = node[0]
            else:
                self.log.error(
                    f"SandbagBuilder: ノード {nid} の位置が取得できません。スキップします。"
                )
                continue

            # Vector 型でなければ変換
            if not isinstance(pos, Vector):
                try:
                    pos = Vector(pos)
                except Exception as e:
                    self.log.error(
                        f"SandbagBuilder: ノード {nid} の位置 Vector 変換失敗: {e}"
                    )
                    continue

            try:
                # Blender のデフォルト立方体サイズ=2 → size=1 で 1辺=2 のキューブを追加
                bpy.ops.mesh.primitive_cube_add(size=1.0, location=pos)
                obj = bpy.context.object
                obj.name = f"Sandbag_{nid}"
                # 個別スケールで cube_size に合わせる
                sx, sy, sz = self.cube_size
                obj.scale = (sx / 2, sy / 2, sz / 2)
                objs[nid] = obj
                self.log.debug(
                    f"Sandbag_{nid} generated at {tuple(pos)} size={self.cube_size}"
                )
            except Exception as e:
                self.log.error(
                    f"SandbagBuilder: ノード {nid} のサンドバッグ生成失敗: {e}"
                )

        self.log.info(f"{len(objs)} 件の Blender サンドバッグを生成しました。")
        return objs
