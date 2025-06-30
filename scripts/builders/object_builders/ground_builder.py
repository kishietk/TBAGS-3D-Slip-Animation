# builders/object_builders/ground_builder.py

"""
ファイル名: builders/object_builders/ground_builder.py

責務:
- Blender 上に地面用平面メッシュを生成し、シーンに配置する。
- サイズ（X,Y）・位置・名前をパラメータ化し、BuilderBase の run() から呼び出せるようにラップ。

TODO:
- テクスチャ／マテリアル初期設定分離
- 高度な地形生成（凹凸・ノイズなど）用の拡張フック追加
"""

import bpy
from typing import Tuple, Optional
from utils import setup_logging
from builders.base import BuilderBase

log = setup_logging("GroundBuilder")


class GroundBuilder(BuilderBase):
    def __init__(
        self,
        size: Tuple[float, float] = (10.0, 10.0),
        location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        name: str = "GroundPlane",
    ):
        """
        初期化:
            size:     (幅, 奥行) で平面のスケールを制御
            location: (X, Y, Z) で配置位置を指定
            name:     作成オブジェクト名
        """
        super().__init__()
        self.size = size
        self.location = location
        self.name = name
        self.log = log

    def build(self) -> Optional[bpy.types.Object]:
        """
        役割:
            指定サイズ・位置で平面メッシュを生成し、シーンにリンクする。
        返り値:
            bpy.types.Object: 生成した平面オブジェクト、失敗時は None
        """
        try:
            # Blender のデフォルト plane_add は size=2 で辺長2の平面
            bpy.ops.mesh.primitive_plane_add(size=1.0, location=self.location)
            obj = bpy.context.object
            obj.name = self.name

            # size=(w, d) に合わせてスケール調整
            sx, sy = self.size
            obj.scale = (sx / 2, sy / 2, 1.0)

            self.log.info(
                f"{self.name} created at {self.location} with size={self.size}"
            )
            return obj
        except Exception as e:
            self.log.error(f"GroundBuilder: 地面の生成に失敗しました: {e}")
            return None
