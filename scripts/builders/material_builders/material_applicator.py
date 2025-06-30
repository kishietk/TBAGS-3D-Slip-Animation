# builders/material_builders/material_applicator.py

"""
ファイル名: builders/material_builders/material_applicator.py

責務:
- シーン内の各オブジェクト群に対し、マテリアルを一括適用する。
- 適用対象（パネル・屋根・柱・梁・ノード・サンドバッグ・地面）ごとに分岐。
"""

import bpy
from typing import Dict, List, Optional, Union, Tuple
from utils import setup_logging
from builders.base import BuilderBase
from .material_factories import (
    create_wall_material,
    create_roof_material,
    create_column_material,
    create_beam_material,
    create_node_material,
    create_sandbag_material,
    create_sandbag_texture_material,
    create_ground_material,
)
from configs.paths import TBAGS_TEXTURE

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

        # サンドバッグ用テクスチャマテリアルを事前生成（タイル数=6に設定）
        try:
            mat_sandbag_tex = create_sandbag_texture_material(
                img_path=TBAGS_TEXTURE,
                alpha=1.0,
                tile=6.0
            )
            use_tex = True
        except Exception as e:
            log.warning(
                f"Sandbag texture load failed ({TBAGS_TEXTURE}): {e} — 緑マテリアルを使用します。"
            )
            mat_sandbag_tex = None
            use_tex = False

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
            if not getattr(obj, "data", None) or not hasattr(obj.data, "materials"):
                log.warning(
                    f"{obj.name} にマテリアルスロットがないためスキップします。"
                )
                continue
            obj.data.materials.clear()
            obj.data.materials.append(mat_wall)
            counts["パネル"] += 1

        # 屋根
        if self.roof_obj:
            if getattr(self.roof_obj, "data", None) and hasattr(
                self.roof_obj.data, "materials"
            ):
                self.roof_obj.data.materials.clear()
                self.roof_obj.data.materials.append(mat_roof)
                counts["屋根"] += 1
            else:
                log.warning(
                    f"{self.roof_obj.name} にマテリアルスロットがないためスキップします。"
                )

        # member_objs がタプルの場合にオブジェクトのみを抽出
        member_objs_clean: List[bpy.types.Object] = []
        for item in self.member_objs:
            if isinstance(item, tuple):
                member_objs_clean.append(item[0])
            else:
                member_objs_clean.append(item)

        # 柱・梁
        for obj in member_objs_clean:
            if not getattr(obj, "data", None) or not hasattr(obj.data, "materials"):
                log.warning(
                    f"{obj.name} にマテリアルスロットがないためスキップします。"
                )
                continue
            obj.data.materials.clear()
            if obj.name.startswith("Column_"):
                obj.data.materials.append(mat_col)
                counts["柱"] += 1
            else:
                obj.data.materials.append(mat_beam)
                counts["梁"] += 1

        # ノード球
        for obj in self.node_objs.values():
            if not getattr(obj, "data", None) or not hasattr(obj.data, "materials"):
                log.warning(
                    f"{obj.name} にマテリアルスロットがないためスキップします。"
                )
                continue
            obj.data.materials.clear()
            obj.data.materials.append(mat_node)
            counts["ノード"] += 1

        # サンドバッグ: Empty 以下の全 Mesh にマテリアル適用
        for base in self.sandbag_objs.values():
            if base.type != "EMPTY":
                continue
            for mesh_obj in base.children_recursive:
                if mesh_obj.type != "MESH" or not getattr(mesh_obj, "data", None):
                    continue
                mat_to_use = mat_sandbag_tex if use_tex else mat_sandbag
                try:
                    mesh_obj.data.materials.clear()
                    mesh_obj.data.materials.append(mat_to_use)
                    counts["サンドバッグ"] += 1
                except Exception as e:
                    log.warning(f"{mesh_obj.name} へのマテリアル適用に失敗: {e}")

        # 地面
        if self.ground_obj:
            if getattr(self.ground_obj, "data", None) and hasattr(
                self.ground_obj.data, "materials"
            ):
                self.ground_obj.data.materials.clear()
                self.ground_obj.data.materials.append(mat_ground)
                counts["地面"] += 1
            else:
                log.warning(
                    f"{self.ground_obj.name} にマテリアルスロットがないためスキップします。"
                )

        # ログ出力
        summary = "、".join(f"{k}:{v}" for k, v in counts.items() if v > 0)
        log.info(f"マテリアル適用完了: [{summary}]")
