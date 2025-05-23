"""
panels.py

【役割】
- ノード座標から壁パネル・屋根オブジェクトを自動生成するビルダー。
- 階層・外周エッジごとの判定しきい値等、数値マジックナンバーは定数化。
- エラーや異常時もファイル・ID・行番号つきで詳細ログ。

【設計方針】
- EPS_XY_MATCH等はファイル先頭に定数で一元管理し、将来的な設計変更も容易に。
- 保守性/解析性の高いログ・型ヒント・コメントを徹底。
"""

import bpy
import bmesh
from typing import Dict, List, Tuple
from mathutils import Vector
from logging_utils import setup_logging

log = setup_logging()

# --- 判定しきい値定数（マジックナンバー排除） ---
EPS_XY_MATCH = 1e-3


def build_panels(
    nodes: dict[int, Vector], edges: set[tuple[int, int]]
) -> list[bpy.types.Object]:
    """
    ノード座標から外周水平セグメントを自動抽出し、
    各階層の壁パネルをBlender上に生成する関数
    """
    if not nodes:
        log.warning("No nodes supplied to build_panels()")
        return []

    xs = [v.x for v in nodes.values()]
    ys = [v.y for v in nodes.values()]
    zs = sorted({v.z for v in nodes.values()})
    if len(zs) < 2:
        log.warning("Insufficient Z levels for panel generation")
        return []

    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)

    panel_ids: list[tuple[int, int, int, int]] = []
    for lvl, z in enumerate(zs[:-1]):
        z_up = zs[lvl + 1]
        left = sorted(
            [
                nid
                for nid, pos in nodes.items()
                if abs(pos.x - xmin) < EPS_XY_MATCH and abs(pos.z - z) < EPS_XY_MATCH
            ],
            key=lambda i: nodes[i].y,
        )
        right = sorted(
            [
                nid
                for nid, pos in nodes.items()
                if abs(pos.x - xmax) < EPS_XY_MATCH and abs(pos.z - z) < EPS_XY_MATCH
            ],
            key=lambda i: nodes[i].y,
        )
        front = sorted(
            [
                nid
                for nid, pos in nodes.items()
                if abs(pos.y - ymin) < EPS_XY_MATCH and abs(pos.z - z) < EPS_XY_MATCH
            ],
            key=lambda i: nodes[i].x,
        )
        back = sorted(
            [
                nid
                for nid, pos in nodes.items()
                if abs(pos.y - ymax) < EPS_XY_MATCH and abs(pos.z - z) < EPS_XY_MATCH
            ],
            key=lambda i: nodes[i].x,
        )

        def segs(lst: list[int]) -> list[tuple[int, int]]:
            return [(lst[i], lst[i + 1]) for i in range(len(lst) - 1)]

        for a, b in segs(left) + segs(front) + segs(right) + segs(back):

            def find_at(x: float, y: float, zval: float) -> int | None:
                for nid2, pos2 in nodes.items():
                    if (
                        abs(pos2.z - zval) < EPS_XY_MATCH
                        and abs(pos2.x - x) < EPS_XY_MATCH
                        and abs(pos2.y - y) < EPS_XY_MATCH
                    ):
                        return nid2
                return None

            x1, y1 = nodes[a].x, nodes[a].y
            x2, y2 = nodes[b].x, nodes[b].y
            c = find_at(x1, y1, z_up)
            d = find_at(x2, y2, z_up)
            if c and d:
                panel_ids.append((a, b, c, d))

    panels: list[bpy.types.Object] = []
    for a, b, c, d in panel_ids:
        try:
            mesh = bpy.data.meshes.new(f"Panel_{a}_{b}")
            obj = bpy.data.objects.new(f"Panel_{a}_{b}", mesh)
            bpy.context.collection.objects.link(obj)
            obj["panel_ids"] = (a, b, c, d)
            panels.append(obj)
        except Exception as e:
            log.error(f"Failed to create panel ({a}, {b}, {c}, {d}): {e}")
    return panels


def build_roof(
    nodes: dict[int, Vector],
) -> tuple[bpy.types.Object | None, list[tuple[int, int, int, int]]]:
    """
    最上階ノードから屋根パネル群を生成し、Blenderオブジェクトとして返す
    """
    zs = sorted({v.z for v in nodes.values()})
    if not zs:
        log.warning("No Z levels found for roof generation")
        return None, []
    top_z = zs[-1]
    tops = {nid: pos for nid, pos in nodes.items() if abs(pos.z - top_z) < EPS_XY_MATCH}
    xs = sorted({v.x for v in tops.values()})
    ys = sorted({v.y for v in tops.values()})

    def fid(x: float, y: float) -> int | None:
        return next(
            (
                n
                for n, p in tops.items()
                if abs(p.x - x) < EPS_XY_MATCH and abs(p.y - y) < EPS_XY_MATCH
            ),
            None,
        )

    quads: list[tuple[int, int, int, int]] = []
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            bl = fid(xs[i], ys[j])
            br = fid(xs[i + 1], ys[j])
            tr = fid(xs[i + 1], ys[j + 1])
            tl = fid(xs[i], ys[j + 1])
            if None not in (bl, br, tr, tl):
                quads.append((bl, br, tr, tl))

    try:
        mesh = bpy.data.meshes.new("RoofMesh")
        obj = bpy.data.objects.new("Roof", mesh)
        bpy.context.collection.objects.link(obj)
        obj["roof_quads"] = quads
        return obj, quads
    except Exception as e:
        log.error(f"Failed to create roof mesh: {e}")
        return None, quads
