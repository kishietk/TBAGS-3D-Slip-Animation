import bpy
import bmesh
from logging_utils import setup_logging

log = setup_logging()


def build_panels(nodes, edges):
    """
    ノード座標から外周水平セグメントを自動抽出し、
    各階層の壁パネルをBlender上に生成する関数

    引数:
        nodes: {nid: Vector}  ノード座標辞書
        edges: set           （未使用。将来の拡張用シグネチャ）

    戻り値:
        panels: [Object, ...] 壁パネルBlenderオブジェクトのリスト

    備考:
        - 各階ごとにX/Y/Z座標から外周4辺を抽出
        - 各辺に対し上階の同座標ノードを検索し、4点でパネルを作成
    """
    if not nodes:
        return []

    # --- 全ノードの座標範囲 ---
    xs = [v.x for v in nodes.values()]
    ys = [v.y for v in nodes.values()]
    zs = sorted({v.z for v in nodes.values()})
    if len(zs) < 2:
        return []

    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)

    panel_ids = []
    # --- 各階層ごとに ---
    for lvl, z in enumerate(zs[:-1]):
        z_up = zs[lvl + 1]

        # 各辺ごとのノードIDリストを抽出
        left = sorted(
            [
                nid
                for nid, pos in nodes.items()
                if abs(pos.x - xmin) < 1e-3 and abs(pos.z - z) < 1e-3
            ],
            key=lambda i: nodes[i].y,
        )
        right = sorted(
            [
                nid
                for nid, pos in nodes.items()
                if abs(pos.x - xmax) < 1e-3 and abs(pos.z - z) < 1e-3
            ],
            key=lambda i: nodes[i].y,
        )
        front = sorted(
            [
                nid
                for nid, pos in nodes.items()
                if abs(pos.y - ymin) < 1e-3 and abs(pos.z - z) < 1e-3
            ],
            key=lambda i: nodes[i].x,
        )
        back = sorted(
            [
                nid
                for nid, pos in nodes.items()
                if abs(pos.y - ymax) < 1e-3 and abs(pos.z - z) < 1e-3
            ],
            key=lambda i: nodes[i].x,
        )

        # 連続ペアを抽出する補助関数
        def segs(lst):
            return [(lst[i], lst[i + 1]) for i in range(len(lst) - 1)]

        for a, b in segs(left) + segs(front) + segs(right) + segs(back):
            # 上階（z_up）に同じX,YのノードがあればID取得
            def find_at(x, y, zval):
                for nid2, pos2 in nodes.items():
                    if (
                        abs(pos2.z - zval) < 1e-3
                        and abs(pos2.x - x) < 1e-3
                        and abs(pos2.y - y) < 1e-3
                    ):
                        return nid2
                return None

            x1, y1 = nodes[a].x, nodes[a].y
            x2, y2 = nodes[b].x, nodes[b].y
            c = find_at(x1, y1, z_up)
            d = find_at(x2, y2, z_up)
            if c and d:
                panel_ids.append((a, b, c, d))

    # --- パネルBlenderオブジェクト化 ---
    panels = []
    for a, b, c, d in panel_ids:
        mesh = bpy.data.meshes.new(f"Panel_{a}_{b}")
        obj = bpy.data.objects.new(f"Panel_{a}_{b}", mesh)
        bpy.context.collection.objects.link(obj)
        obj["panel_ids"] = (a, b, c, d)  # 4点のノードIDを属性に記録
        panels.append(obj)
    return panels


def build_roof(nodes):
    """
    最上階ノードから屋根パネル群を生成し、Blenderオブジェクトとして返す

    引数:
        nodes: {nid: Vector}

    戻り値:
        (roof_obj, quads)
        - roof_obj: 屋根Blenderオブジェクト
        - quads: [(bl, br, tr, tl), ...] 各屋根パネルのノードIDタプル
    """
    zs = sorted({v.z for v in nodes.values()})
    if not zs:
        return None, []
    top_z = zs[-1]
    # 最上階ノードを抽出
    tops = {nid: pos for nid, pos in nodes.items() if abs(pos.z - top_z) < 1e-3}
    xs = sorted({v.x for v in tops.values()})
    ys = sorted({v.y for v in tops.values()})

    # 座標値からノードIDを逆引き
    def fid(x, y):
        return next(
            (n for n, p in tops.items() if abs(p.x - x) < 1e-3 and abs(p.y - y) < 1e-3),
            None,
        )

    quads = []
    # グリッド上で四角形を生成
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            bl = fid(xs[i], ys[j])
            br = fid(xs[i + 1], ys[j])
            tr = fid(xs[i + 1], ys[j + 1])
            tl = fid(xs[i], ys[j + 1])
            if None not in (bl, br, tr, tl):
                quads.append((bl, br, tr, tl))

    # 屋根メッシュ・オブジェクト生成
    mesh = bpy.data.meshes.new("RoofMesh")
    obj = bpy.data.objects.new("Roof", mesh)
    bpy.context.collection.objects.link(obj)
    obj["roof_quads"] = quads  # どのノードで構成されるか属性で保持
    return obj, quads
