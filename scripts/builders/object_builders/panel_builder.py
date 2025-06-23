# builders/object_builders/panel_builder.py

"""
ファイル名: builders/object_builders/panel_builder.py

責務:
- コア Panel リストから Blender 壁パネルオブジェクトを生成する。
- 頂点数が 4 以外のパネルはスキップし、生成失敗時はログに記録のみ行う。
- アニメーション・マテリアル処理は含まない。

TODO:
- 不正形状パネルや多角形対応
- UV／マテリアル適用ロジックの分離
"""

import bpy
from typing import List, Any
from utils.logging_utils import setup_logging
from builders.base import BuilderBase

log = setup_logging("PanelBuilder")


class PanelBuilder(BuilderBase):
    def __init__(self, panels: List[Any], name_prefix: str = "Panel"):
        """
        初期化:
            panels: List[Panel] オブジェクトのリスト
            name_prefix: 生成オブジェクト名のプレフィクス
        """
        super().__init__()
        self.panels = panels
        self.name_prefix = name_prefix
        self.log = log

    def build(self) -> List[bpy.types.Object]:
        """
        役割:
            各 Panel の頂点・面情報からメッシュを生成し、シーンに配置する。

        返り値:
            List[bpy.types.Object]: 生成されたパネルオブジェクトのリスト
        """
        if not self.panels:
            self.log.warning("PanelBuilder: パネルデータが空です。スキップします。")
            return []

        blender_objs: List[bpy.types.Object] = []
        self.log.info("===== パネル生成開始 =====")
        for panel in self.panels:
            try:
                # ノードから頂点座標を抽出
                verts = [n.pos for n in panel.nodes]
                if len(verts) != 4:
                    self.log.warning(
                        f"Panel {panel.id}: 4ノード以外は生成不可 (nodes={len(verts)})"
                    )
                    continue

                # メッシュ／オブジェクト作成
                mesh = bpy.data.meshes.new(f"{self.name_prefix}_{panel.id}")
                obj = bpy.data.objects.new(f"{self.name_prefix}_{panel.id}", mesh)
                bpy.context.collection.objects.link(obj)

                # Blender 用座標リストと面情報
                verts_bl = [tuple(v) for v in verts]
                faces = [(0, 1, 2, 3)]
                mesh.from_pydata(verts_bl, [], faces)
                mesh.update()

                # メタデータとしてパネル ID・種別・階数を格納
                obj["panel_ids"] = [n.id for n in panel.nodes]
                obj["panel_kind"] = panel.kind
                if hasattr(panel, "floor"):
                    obj["panel_floor"] = panel.floor

                blender_objs.append(obj)
                self.log.debug(f"{self.name_prefix}_{panel.id} を生成しました。")
            except Exception as e:
                self.log.error(f"PanelBuilder: Panel {panel.id} 生成失敗: {e}")

        self.log.info(f"{len(blender_objs)} 件のパネルオブジェクトを生成しました。")
        return blender_objs
