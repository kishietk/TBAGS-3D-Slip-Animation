# パネル・屋根生成ビルダー
# Panelコアデータから壁パネル・屋根パネルをBlender上に生成する

import bpy
from mathutils import Vector
from utils.logging_utils import setup_logging
from config import EPS_XY_MATCH

log = setup_logging()


def build_blender_panels(panels: list) -> list:  # List[Panel]
    """
    コアPanelリストからBlender上に壁パネルを生成する
    引数:
        panels: Panelインスタンスのリスト
    戻り値:
        パネルのBlenderオブジェクトリスト
    """
    if not panels:
        log.warning("No Panel data supplied to build_blender_panels()")
        return []

    blender_objs = []
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
            faces = [(0, 1, 2, 3)]  # この順で作成

            mesh.from_pydata(verts_bl, [], faces)
            mesh.update()

            obj["panel_ids"] = [n.id for n in panel.nodes]  # [a, b, d, c]の順
            obj["panel_kind"] = panel.kind
            if hasattr(panel, "floor"):
                obj["panel_floor"] = panel.floor
            blender_objs.append(obj)
            log.debug(
                f"Created Panel_{panel.id}: panel_ids={[n.id for n in panel.nodes]}"
            )
        except Exception as e:
            log.error(f"Failed to create panel ({panel}): {e}")
    log.info(
        f"build_blender_panels: {len(blender_objs)} Blender panels created from core data"
    )
    return blender_objs


# build_roofは変更不要


def build_roof(
    nodes: dict[int, Vector],
) -> tuple:
    """
    最上階ノードから屋根パネル群を生成し、Blenderオブジェクトとして返す
    引数:
        nodes: ノードID→座標Vectorの辞書
    戻り値:
        (屋根オブジェクト, 屋根パネルIDタプルリスト)
    """
    zs = sorted({v.z for v in nodes.values()})
    if not zs:
        log.warning("No Z levels found for roof generation")
        return None, []
    top_z = zs[-1]
    tops = {nid: pos for nid, pos in nodes.items() if abs(pos.z - top_z) < EPS_XY_MATCH}
    xs = sorted({v.x for v in tops.values()})
    ys = sorted({v.y for v in tops.values()})

    def fid(x, y):
        return next(
            (
                n
                for n, p in tops.items()
                if abs(p.x - x) < EPS_XY_MATCH and abs(p.y - y) < EPS_XY_MATCH
            ),
            None,
        )

    quads = []
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
        # 頂点座標リストを作成
        verts = [tops[nid] for nid in tops]
        # facesは作成済みquadリストを利用（順番が一致していれば）
        mesh.update()
        obj["roof_quads"] = quads
        log.debug(f"Created Roof: {obj.name}, quads={quads}")
        return obj, quads
    except Exception as e:
        log.error(f"Failed to create roof mesh: {e}")
        return None, quads
