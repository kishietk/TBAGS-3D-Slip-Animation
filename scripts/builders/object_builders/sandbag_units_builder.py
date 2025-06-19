"""
ファイル名: builders/object_builders/sandbag_units_builder.py

責務:
- 指定ユニット（unit_id→[sandbag_id,…]）ごとに Collection を作成し、
  それぞれのサンドバッグオブジェクトをまとめる。

TODO:
- 空ユニット時の挙動を調整
- Collection への重複リンク回避
"""

import bpy
from utils.logging_utils import setup_logging
from builders.base import BuilderBase


class SandbagUnitsBuilder(BuilderBase):

    def __init__(
        self,
        units: dict[int, list[int]],
        sandbags_objs: dict[int, bpy.types.Object],
    ):

        """初期化: units は {unit_id: [sandbag_id,...]} 形式とする。"""
        super().__init__()
        self.units = units
        self.sandbags_objs = sandbags_objs
        self.log = setup_logging("SandbagUnitsBuilder")

    def build(self) -> dict[int, bpy.types.Collection]:
        """
        役割:
            指定ユニットごとにコレクションを作成し、対応するサンドバッグをまとめる。

        返り値:
            {unit_id: Blenderコレクション}
        """
        collections: dict[int, bpy.types.Collection] = {}
        for uid, sb_ids in self.units.items():
            col = bpy.data.collections.new(f"SandbagUnit_{uid}")
            bpy.context.scene.collection.children.link(col)
            for sbid in sb_ids:
                obj = self.sandbags_objs.get(sbid)
                if obj:
                    col.objects.link(obj)
            collections[uid] = col
            self.log.debug(f"Unit_{uid} collection created with {len(sb_ids)} sandbags")
        self.log.info(f"{len(collections)} sandbag units built.")
        return collections
