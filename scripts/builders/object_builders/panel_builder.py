# builders/object_builders/panel_builder.py

import bpy
from typing import List
from utils import setup_logging
from builders.base import BuilderBase
from builders.builder_registry import register_builder
from cores.entities import Panel
from configs import PANEL_VERT_COUNT, PANEL_OBJ_PREFIX

log = setup_logging("PanelBuilder")


class PanelBuilder(BuilderBase):
    """
    コアPanelリストからBlender壁パネルオブジェクトを生成するビルダー。
    """

    def __init__(self, panels: List[Panel], name_prefix: str = PANEL_OBJ_PREFIX):
        super().__init__()
        self.panels = panels
        self.name_prefix = name_prefix

    def build(self) -> List[bpy.types.Object]:
        objs: List[bpy.types.Object] = []
        for panel in self.panels:
            verts = [n.pos for n in panel.nodes]
            if len(verts) != PANEL_VERT_COUNT:
                log.warning(f"Panel {panel.id}: invalid node count {len(verts)}")
                continue
            # メッシュ作成
            mesh = bpy.data.meshes.new(f"{self.name_prefix}{panel.id}")
            obj = bpy.data.objects.new(f"{self.name_prefix}{panel.id}", mesh)
            bpy.context.collection.objects.link(obj)
            mesh.from_pydata([tuple(v) for v in verts], [], [(0, 1, 2, 3)])
            mesh.update()
            objs.append(obj)
        return objs


@register_builder(Panel)
def build_panel(scene_builder, panel: Panel, ctx):
    """
    SceneBuilder から要素単位で呼び出されるラッパー。
    PanelBuilder はリスト対応なので、単一要素をリストに詰める。
    """
    # ctx は辞書ですが使用しません
    return PanelBuilder([panel]).build()
