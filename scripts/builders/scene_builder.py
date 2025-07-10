# scene_builder.py
from typing import Dict, List, Tuple, Optional, Any
from utils import setup_logging
from builders.base import BuilderBase
from builders.builder_registry import get_builder
from builders.build_context import BuildContext
from configs import SPHERE_RADIUS
import bpy

log = setup_logging("SceneBuilder")


class SceneBuilder(BuilderBase):
    def __init__(self, core: Any, include_ground: bool = True):
        super().__init__()
        self.core = core
        self.include_ground = include_ground

    def build(
        self,
    ) -> Tuple[
        Dict[int, bpy.types.Object],
        List[bpy.types.Object],
        Optional[bpy.types.Object],
        List[Tuple[int, int, int, int]],
        List[Tuple[bpy.types.Object, int, int]],
        Optional[bpy.types.Object],
    ]:
        # Coreから取得
        nodes = self.core.nodes or {}
        panels = self.core.panels or []
        columns = self.core.columns or []
        beams = self.core.beams or []
        roof = getattr(self.core, "roof", None)
        ground = getattr(self.core, "ground", None)

        log.info(
            f"Building scene with {len(nodes)} nodes, {len(panels)} panels, "
            f"{len(columns)} columns, {len(beams)} beams, "
            f"Roof={'Yes' if roof else 'No'}, Ground={'Yes' if ground else 'No'}"
        )

        # 基本コンテキストと座標マップ
        base_ctx = self._build_ctx()
        positions = {nid: data.pos for nid, data in nodes.items()}

        # 1. ノード生成
        node_objs: Dict[int, bpy.types.Object] = {}
        for nid, node in nodes.items():
            builder = get_builder(node)
            if not builder:
                continue
            created = builder(self, node, base_ctx)
            if isinstance(created, dict):
                node_objs.update(created)
            elif isinstance(created, bpy.types.Object):
                node_objs[nid] = created

        # 2. パネル生成
        panel_objs: List[bpy.types.Object] = []
        for panel in panels:
            builder = get_builder(panel)
            if not builder:
                continue
            created = builder(self, panel, base_ctx)
            if isinstance(created, list):
                panel_objs.extend(created)
            elif isinstance(created, bpy.types.Object):
                panel_objs.append(created)

        # 3. 屋根生成
        roof_obj: Optional[bpy.types.Object] = None
        roof_quads: List[Tuple[int, int, int, int]] = []
        if roof:
            builder = get_builder(roof)
            if builder:
                roof_obj, roof_quads = builder(
                    self, roof, self._build_ctx(positions=positions)
                )

        # 4. 柱・梁生成
        extra_ctx = {"edges": set(columns + beams), "thickness": 0.5}
        ctx_members = self._build_ctx(positions=positions, extra=extra_ctx)
        member_objs: List[Tuple[bpy.types.Object, int, int]] = []

        for edge in columns + beams:
            builder = get_builder(edge)
            if not builder:
                continue
            created = builder(self, edge, ctx_members)
            if isinstance(created, dict):
                for key, obj in created.items():
                    a, b = map(int, key.split("_"))
                    member_objs.append((obj, a, b))
            elif isinstance(created, list):
                member_objs.extend(created)

        # 5. 地面生成
        ground_obj: Optional[bpy.types.Object] = None
        if self.include_ground and ground:
            builder = get_builder(ground)
            if builder:
                created = builder(self, ground, base_ctx)
                if isinstance(created, bpy.types.Object):
                    ground_obj = created

        # 6. サマリー
        summary = (
            f"SceneBuilder Summary: Nodes={len(node_objs)}, "
            f"Panels={len(panel_objs)}, RoofQuads={len(roof_quads)}, "
            f"Members={len(member_objs)}, Ground={'Yes' if ground_obj else 'No'}"
        )
        log.info(summary)

        return node_objs, panel_objs, roof_obj, roof_quads, member_objs, ground_obj

    def _build_ctx(self, positions=None, extra=None):
        """
        BuildContextを生成。positions/extraは上書き可能。
        """
        return BuildContext(
            scene=bpy.context.scene,
            positions=positions
            or {nid: data.pos for nid, data in getattr(self.core, "nodes", {}).items()},
            core=self.core,
            extra=extra or {},
        )
