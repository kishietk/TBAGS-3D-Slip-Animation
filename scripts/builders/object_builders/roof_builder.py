import bpy
from mathutils import Vector
from typing import Dict, Tuple, List, Optional
from utils import setup_logging
from builders.base import BuilderBase
from builders.builder_registry import register_builder
from cores import Panel, Roof
from configs import EPS_XY_MATCH, ROOF_OBJ_NAME

log = setup_logging("RoofBuilder")


class RoofBuilder(BuilderBase):
    """
    最上階ノード群から屋根パネル（四角形クワッド）を抽出し、Blenderオブジェクトとして生成するビルダー。
    """

    def __init__(self, nodes: Dict[int, Vector], name: str = ROOF_OBJ_NAME):
        super().__init__()
        self.nodes = nodes
        self.name = name

    def build(
        self,
    ) -> Tuple[Optional[bpy.types.Object], List[Tuple[int, int, int, int]]]:
        zs = sorted({v.z for v in self.nodes.values()})
        if not zs:
            log.warning("RoofBuilder: No Z levels found")
            return None, []
        top_z = zs[-1]
        tops = {
            nid: pos
            for nid, pos in self.nodes.items()
            if abs(pos.z - top_z) < EPS_XY_MATCH
        }

        xs = sorted({v.x for v in tops.values()})
        ys = sorted({v.y for v in tops.values()})

        def fid(x: float, y: float) -> Optional[int]:
            return next(
                (
                    nid
                    for nid, pos in tops.items()
                    if abs(pos.x - x) < EPS_XY_MATCH and abs(pos.y - y) < EPS_XY_MATCH
                ),
                None,
            )

        quads: List[Tuple[int, int, int, int]] = []
        for i in range(len(xs) - 1):
            for j in range(len(ys) - 1):
                bl = fid(xs[i], ys[j])
                br = fid(xs[i + 1], ys[j])
                tr = fid(xs[i + 1], ys[j + 1])
                tl = fid(xs[i], ys[j + 1])
                if None not in (bl, br, tr, tl):
                    quads.append((bl, br, tr, tl))
                    log.debug(f"Roof quad: {bl}-{br}-{tr}-{tl}")

        try:
            mesh = bpy.data.meshes.new(f"{self.name}Mesh")
            obj = bpy.data.objects.new(self.name, mesh)
            bpy.context.collection.objects.link(obj)
            obj["roof_quads"] = quads
            log.info(f"RoofBuilder: Created {self.name} with {len(quads)} quads")
            return obj, quads
        except Exception as e:
            log.error(f"RoofBuilder: Failed to create roof object: {e}")
            return None, quads


@register_builder(Roof)
def build_roof(scene_builder, roof_panel: Roof, ctx):
    """
    SceneBuilder から要素単位で呼び出されるビルダー。
    Roof クラスまたは Panel.kind == 'roof' のものを RoofBuilder で処理。
    """
    # 型チェック: Roof または kind プロパティで判定
    if not isinstance(roof_panel, Roof) and getattr(roof_panel, "kind", "") != "roof":
        return None, []
    # ノードID→Vector マッピングを作成
    nodes_map = {n.id: n.pos for n in roof_panel.nodes}
    return RoofBuilder(nodes_map).build()
