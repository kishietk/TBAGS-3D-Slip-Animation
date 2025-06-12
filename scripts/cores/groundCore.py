"""
cores/groundCore.py

責務:
- 地面（Ground）モデル情報の保持・管理
- 物理位置、Blenderオブジェクト参照、追加属性（地震データなど）の付与

設計指針:
- 生成したBlenderオブジェクトとコアモデルを分離しつつ、相互参照を保持
- 拡張：今後地面に高さ・テクスチャ・物理性・地震アニメの設定等を追加する基盤

使用例:
    from cores.groundCore import Ground
    ground = Ground(size=30.0)
    ground.set_blender_object(obj)
"""

from typing import Optional, Dict, Any
from mathutils import Vector


class Ground:
    """
    地面コアモデルクラス
    - 基本的な地面属性とBlenderオブジェクト参照を保持

    属性:
        size (float): 地面の一辺長さ
        position (Vector): 現在位置（アニメ用）
        blender_object (bpy.types.Object or None): Blenderオブジェクト参照
        attributes (dict): 任意の追加属性
    """

    def __init__(self, size: float = 30.0, position: Optional[Vector] = None):
        self.size = size
        self.position = position or Vector((0, 0, 0))
        self.blender_object = None  # Blender側のオブジェクト参照
        self.attributes: Dict[str, Any] = {}

    def set_blender_object(self, obj):
        """
        Blenderオブジェクト参照をセット

        Args:
            obj: bpy.types.Object
        Returns:
            None
        """
        self.blender_object = obj

    def set_attribute(self, key: str, value: Any):
        """
        任意属性の追加・更新

        Args:
            key (str): 属性名
            value (Any): 属性値
        Returns:
            None
        """
        self.attributes[key] = value

    def get_attribute(self, key: str, default=None):
        """
        任意属性の取得

        Args:
            key (str): 属性名
            default: デフォルト値
        Returns:
            値またはdefault
        """
        return self.attributes.get(key, default)

    def __repr__(self):
        return f"Ground(size={self.size}, position={tuple(self.position)}, blender_object={self.blender_object})"
