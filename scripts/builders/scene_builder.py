import bpy
from typing import Any, Dict, List, Tuple, Optional
from utils import setup_logging
from builders.base import BuilderBase
from builders.builder_registry import get_builder
from builders.object_builders.ground_builder import GroundBuilder
from cores import Panel, Roof
from collections.abc import Mapping

log = setup_logging("SceneBuilder")


class SceneBuilder(BuilderBase):
    """
    シーン構築クラス。
    CoreFactory から得られる core.nodes, core.edges, core.panels を元に
    Blender オブジェクトを生成し、以下のタプルを返す。

      (
        node_objs: Dict[int, Object],
        panel_objs: List[Object],
        roof_obj: Optional[Object],
        roof_quads: List[Tuple[int,int,int,int]],
        member_objs: List[Object],  # 梁・柱
        ground_obj: Optional[Object],
      )
    """

    def __init__(
        self,
        core: Any,
        include_ground: bool = True,
        context: Dict[str, Any] = None,
    ):
        super().__init__()
        self.core = core
        self.include_ground = include_ground
        self.context = context or {}

    def build(
        self,
    ) -> Tuple[
        Dict[int, bpy.types.Object],
        List[bpy.types.Object],
        Optional[bpy.types.Object],
        List[Tuple[int, int, int, int]],
        List[bpy.types.Object],
        Optional[bpy.types.Object],
    ]:
        # --- 1. Core から元データ取得 ---
        raw_nodes = getattr(self.core, "nodes", {})
        nodes = (
            raw_nodes.values() if isinstance(raw_nodes, Mapping) else raw_nodes or []
        )

        raw_edges = getattr(self.core, "edges", {})
        edges = (
            raw_edges.values() if isinstance(raw_edges, Mapping) else raw_edges or []
        )

        panels = getattr(self.core, "panels", []) or []

        # --- 2. ノード位置情報をコンテキストにセット ---
        positions = {n.id: n.pos for n in nodes}
        self.context["positions"] = positions

        # --- 3. ノード生成 ---
        node_objs: Dict[int, bpy.types.Object] = {}
        for node in nodes:
            builder = get_builder(node)
            if not builder:
                continue
            created = builder(self, node, self.context)
            if isinstance(created, dict):
                for nid, obj in created.items():
                    node_objs[nid] = obj
            elif created:
                nid = getattr(node, "id", None)
                if nid is not None:
                    node_objs[nid] = created

        # --- 4. 梁・柱 (member) 生成 ---
        member_objs: List[bpy.types.Object] = []
        for edge in edges:
            builder = get_builder(edge)
            if not builder:
                continue
            created = builder(self, edge, self.context)
            if isinstance(created, dict):
                member_objs.extend(created.values())
            elif created:
                member_objs.append(created)

        # --- 5. 壁パネル生成 ---
        panel_objs: List[bpy.types.Object] = []
        for panel in panels:
            # Roof インスタンス or kind が roof は後でまとめて処理
            if isinstance(panel, Roof) or getattr(panel, "kind", "") == "roof":
                continue
            builder = get_builder(panel)
            if not builder:
                continue
            created = builder(self, panel, self.context)
            if isinstance(created, list):
                panel_objs.extend(created)
            elif created:
                panel_objs.append(created)

        # --- 6. 屋根パネル (roof) 生成 ---
        roof_obj: Optional[bpy.types.Object] = None
        roof_quads: List[Tuple[int, int, int, int]] = []
        for panel in panels:
            # Roof インスタンス or kind が roof のパネルを処理
            if not (isinstance(panel, Roof) or getattr(panel, "kind", "") == "roof"):
                continue
            builder = get_builder(panel)
            if not builder:
                continue
            created = builder(self, panel, self.context)
            if isinstance(created, tuple) and created[0] is not None:
                roof_obj, roof_quads = created
                break

        # --- 7. 地面 (ground) 生成 ---
        ground_obj: Optional[bpy.types.Object] = None
        if self.include_ground:
            ground_builder = GroundBuilder()
            ground_obj = ground_builder.build()

        # --- 8. サマリログ ---
        log.info(
            f"SceneBuilder Summary: "
            f"Nodes={len(node_objs)}, "
            f"Members={len(member_objs)}, "
            f"Panels={len(panel_objs)}, "
            f"Roof={'Yes' if roof_obj else 'No'}, "
            f"Ground={'Yes' if ground_obj else 'No'}"
        )

        return node_objs, panel_objs, roof_obj, roof_quads, member_objs, ground_obj
