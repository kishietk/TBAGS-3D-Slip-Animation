# builders/material_builders/material_applicator.py

"""
ファイル名: builders/material_builders/material_applicator.py

責務:
- シーン内の各オブジェクト群に対し、マテリアルを一括適用する。
- 適用対象（パネル・屋根・柱・梁・ノード・サンドバッグ・地面）ごとに分岐。
"""

import bpy
from typing import Dict, List, Optional, Union, Tuple
from utils.logging_utils import setup_logging
from builders.base import BuilderBase
from .material_factories import (
    create_wall_material,
    create_roof_material,
    create_column_material,
    create_beam_material,
    create_node_material,
    create_sandbag_material,
    create_ground_material,
)

log = setup_logging("MaterialApplicator")


class MaterialApplicator(BuilderBase):
    def __init__(
        self,
        node_objs: Dict[int, bpy.types.Object],
        sandbag_objs: Dict[int, bpy.types.Object],
        panel_objs: List[bpy.types.Object],
        roof_obj: Optional[bpy.types.Object],
        member_objs: List[Union[bpy.types.Object, Tuple[bpy.types.Object, int, int]]],
        ground_obj: Optional[bpy.types.Object],
    ):
        super().__init__()
        self.node_objs = node_objs
        self.sandbag_objs = sandbag_objs
        self.panel_objs = panel_objs
        self.roof_obj = roof_obj
        self.member_objs = member_objs
        self.ground_obj = ground_obj

    def build(self) -> None:
        """
        役割:
            各オブジェクト群に対応するマテリアルを適用し、適用件数をログ出力。
        """
        # マテリアル生成
        mat_wall = create_wall_material()
        mat_roof = create_roof_material()
        mat_col = create_column_material()
        mat_beam = create_beam_material()
        mat_node = create_node_material()
        mat_sandbag = create_sandbag_material()
        mat_ground = create_ground_material()

        # カウント用
        counts = {
            "パネル": 0,
            "屋根": 0,
            "柱": 0,
            "梁": 0,
            "ノード": 0,
            "サンドバッグ": 0,
            "地面": 0,
        }

        # 壁パネル
        for obj in self.panel_objs:
            obj.data.materials.clear()
            obj.data.materials.append(mat_wall)
            counts["パネル"] += 1

        # 屋根
        if self.roof_obj:
            self.roof_obj.data.materials.clear()
            self.roof_obj.data.materials.append(mat_roof)
            counts["屋根"] += 1

        # member_objs がタプルの場合にオブジェクトのみを抽出
        member_objs_clean: List[bpy.types.Object] = []
        for item in self.member_objs:
            if isinstance(item, tuple):
                member_objs_clean.append(item[0])
            else:
                member_objs_clean.append(item)

        # 柱・梁
        for obj in member_objs_clean:
            obj.data.materials.clear()
            if obj.name.startswith("Column_"):
                obj.data.materials.append(mat_col)
                counts["柱"] += 1
            elif obj.name.startswith("Beam_"):
                obj.data.materials.append(mat_beam)
                counts["梁"] += 1
            else:
                # 規則外は梁扱い
                obj.data.materials.append(mat_beam)
                counts["梁"] += 1
                log.warning(f"{obj.name} が柱・梁規則に一致せず、梁マテリアル適用")

        # ノード球
        for obj in self.node_objs.values():
            obj.data.materials.clear()
            obj.data.materials.append(mat_node)
            counts["ノード"] += 1

        # サンドバッグ
        for obj in self.sandbag_objs.values():
            obj.data.materials.clear()
            obj.data.materials.append(mat_sandbag)
            counts["サンドバッグ"] += 1

        # 地面
        if self.ground_obj:
            self.ground_obj.data.materials.clear()
            self.ground_obj.data.materials.append(mat_ground)
            counts["地面"] += 1

        # ログ出力
        summary = "、".join(f"{k}:{v}" for k, v in counts.items() if v > 0)
        log.info(f"マテリアル適用完了: [{summary}]")
