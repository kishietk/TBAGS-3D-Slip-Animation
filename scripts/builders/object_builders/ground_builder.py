import bpy
from typing import Tuple, Optional
from utils import setup_logging
from builders.base import BuilderBase
from configs import (
    GROUND_SIZE_XY,
    GROUND_LOCATION,
    GROUND_NAME,
    GROUND_PRIMITIVE_SIZE,
)

log = setup_logging("GroundBuilder")


class GroundBuilder(BuilderBase):
    def __init__(
        self,
        size: Tuple[float, float] = GROUND_SIZE_XY,
        location: Tuple[float, float, float] = GROUND_LOCATION,
        name: str = GROUND_NAME,
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
            # デフォルトプリミティブサイズは定数から
            bpy.ops.mesh.primitive_plane_add(
                size=GROUND_PRIMITIVE_SIZE, location=self.location
            )
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
