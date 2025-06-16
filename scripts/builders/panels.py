"""
ファイル名: builders/panels.py

責務:
- コアPanelリストからBlender壁パネル・屋根オブジェクトを生成する。
- 4ノード以外のPanelや生成失敗時はログに記録し、復帰は担わない。
- 屋根は最上階ノード群から自動生成。

注意点:
- Panelは4ノードのみ対応、他はスキップ
- 屋根はZ最上位・格子パターン前提
- 例外時はエラーログ出力のみ（raiseしない）

TODO:
- パネル/屋根生成汎用化（不正パネル・変則形状対応）
- quad探索部/face生成部の切り出し・型安全化
- オブジェクト属性一元管理・メタデータ分離
"""

import bpy
from mathutils import Vector
from typing import List, Dict, Tuple, Any, Optional
from utils.logging_utils import setup_logging
from configs import EPS_XY_MATCH

log = setup_logging("build_panels")


def build_blender_panels(
    panels: List[Any],  # List[Panel]
) -> List[bpy.types.Object]:
    """
    役割:
        コアPanelリストからBlender上に壁パネルを生成する。

    引数:
        panels (List[Panel]): Panelインスタンスのリスト

    返り値:
        List[bpy.types.Object]: パネルのBlenderオブジェクトリスト

    注意:
        - 4ノードPanel以外は生成不可（スキップ・警告のみ）
    """
    if not panels:
        log.warning("No Panel data supplied to build_blender_panels()")
        return []

    blender_objs: List[bpy.types.Object] = []
    for panel in panels:
        try:
            verts = [n.pos for n in panel.nodes]
            if len(verts) != 4:
                log.warning(
                    f"Panel {panel.id}: 4ノード以外のPanelはBlender生成不可 (nodes={len(verts)})"
                )
                continue

            mesh = bpy.data.meshes.new(f"Panel_{panel.id}")
            obj = bpy.data.objects.new(f"Panel_{panel.id}", mesh)
            bpy.context.collection.objects.link(obj)

            verts_bl = [tuple(v) for v in verts]
            faces = [(0, 1, 2, 3)]

            mesh.from_pydata(verts_bl, [], faces)
            mesh.update()

            obj["panel_ids"] = [n.id for n in panel.nodes]
            obj["panel_kind"] = panel.kind
            if hasattr(panel, "floor"):
                obj["panel_floor"] = panel.floor
            blender_objs.append(obj)
            log.debug(
                f"Created Panel_{panel.id}: panel_ids={[n.id for n in panel.nodes]}"
            )
        except Exception as e:
            log.error(f"Failed to create panel ({panel}): {e}")

    log.info(f"{len(blender_objs)}件のBlender壁オブジェクトを生成しました。")
    return blender_objs


def build_roof(
    nodes: Dict[int, Vector],
) -> Tuple[Optional[bpy.types.Object], List[Tuple[int, int, int, int]]]:
    """
    役割:
        最上階ノードから屋根パネル群を生成し、Blenderオブジェクトとして返す。

    引数:
        nodes (Dict[int, Vector]): ノードID→座標Vectorの辞書

    返り値:
        Tuple[Optional[bpy.types.Object], List[Tuple[int,int,int,int]]]:
            (屋根オブジェクト, 屋根パネルIDタプルリスト)

    注意:
        - Z最大値層のノード格子に対してのみ対応
        - 順序・四角形整合等は盤面前提（不正形状は今後対応）
    """
    zs = sorted({v.z for v in nodes.values()})
    if not zs:
        log.warning("No Z levels found for roof generation")
        return None, []
    top_z = zs[-1]
    tops = {nid: pos for nid, pos in nodes.items() if abs(pos.z - top_z) < EPS_XY_MATCH}
    xs = sorted({v.x for v in tops.values()})
    ys = sorted({v.y for v in tops.values()})

    def fid(x: float, y: float) -> Optional[int]:
        return next(
            (
                n
                for n, p in tops.items()
                if abs(p.x - x) < EPS_XY_MATCH and abs(p.y - y) < EPS_XY_MATCH
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
        mesh = bpy.data.meshes.new("RoofMesh")
        obj = bpy.data.objects.new("Roof", mesh)
        bpy.context.collection.objects.link(obj)
        mesh.update()
        obj["roof_quads"] = quads
        log.debug(f"Created Roof: {obj.name}, quads={quads}")
        log.info("Blenderパネル(屋根)を生成しました。")
        return obj, quads
    except Exception as e:
        log.error(f"Failed to create roof mesh: {e}")
        return None, quads
