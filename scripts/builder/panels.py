import bpy, bmesh
from logging_utils import setup_logging
log = setup_logging()

def build_panels(nodes, edges):
    """
    ノード座標だけから外周水平セグメントを抽出→全階層の壁パネルを生成
      - nodes: {nid: Vector}
      - edges_unused: 接合用エッジ（使いませんがシグネチャ上受け取ります）
    """
    if not nodes:
        return []

    # 座標一覧
    xs = [v.x for v in nodes.values()]
    ys = [v.y for v in nodes.values()]
    zs = sorted({v.z for v in nodes.values()})
    if len(zs) < 2:
        return []

    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)

    panel_ids = []
    # 各階（最下→上）について
    for lvl, z in enumerate(zs[:-1]):
        z_up = zs[lvl + 1]
        # 四辺の境界リスト作成
        left = sorted([nid for nid, pos in nodes.items() if abs(pos.x - xmin) < 1e-3 and abs(pos.z - z) < 1e-3], key=lambda i: nodes[i].y)
        right = sorted([nid for nid, pos in nodes.items() if abs(pos.x - xmax) < 1e-3 and abs(pos.z - z) < 1e-3], key=lambda i: nodes[i].y)
        front = sorted([nid for nid, pos in nodes.items() if abs(pos.y - ymin) < 1e-3 and abs(pos.z - z) < 1e-3], key=lambda i: nodes[i].x)
        back = sorted([nid for nid, pos in nodes.items() if abs(pos.y - ymax) < 1e-3 and abs(pos.z - z) < 1e-3], key=lambda i: nodes[i].x)

        # 連続ペアを抽出
        def segs(lst):
            return [(lst[i], lst[i + 1]) for i in range(len(lst) - 1)]

        for a, b in segs(left) + segs(front) + segs(right) + segs(back):
            # 上階に対応するノードを探す
            def find_at(x, y, zval):
                for nid2, pos2 in nodes.items():
                    if abs(pos2.z - zval) < 1e-3 and abs(pos2.x - x) < 1e-3 and abs(pos2.y - y) < 1e-3:
                        return nid2
                return None

            x1, y1 = nodes[a].x, nodes[a].y
            x2, y2 = nodes[b].x, nodes[b].y
            c = find_at(x1, y1, z_up)
            d = find_at(x2, y2, z_up)
            if c and d:
                panel_ids.append((a, b, c, d))

    # オブジェクト化
    panels = []
    for a, b, c, d in panel_ids:
        mesh = bpy.data.meshes.new(f"Panel_{a}_{b}")
        obj = bpy.data.objects.new(f"Panel_{a}_{b}", mesh)
        bpy.context.collection.objects.link(obj)
        obj["panel_ids"] = (a, b, c, d)
        panels.append(obj)
    return panels

def build_roof(nodes):
    zs = sorted({v.z for v in nodes.values()})
    if not zs:
        return None, []
    top_z = zs[-1]
    tops = {nid: pos for nid, pos in nodes.items() if abs(pos.z - top_z) < 1e-3}
    xs = sorted({v.x for v in tops.values()})
    ys = sorted({v.y for v in tops.values()})

    def fid(x, y):
        return next((n for n, p in tops.items() if abs(p.x - x) < 1e-3 and abs(p.y - y) < 1e-3), None)

    quads = []
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            bl = fid(xs[i], ys[j])
            br = fid(xs[i + 1], ys[j])
            tr = fid(xs[i + 1], ys[j + 1])
            tl = fid(xs[i], ys[j + 1])
            if None not in (bl, br, tr, tl):
                quads.append((bl, br, tr, tl))

    mesh = bpy.data.meshes.new("RoofMesh")
    obj = bpy.data.objects.new("Roof", mesh)
    bpy.context.collection.objects.link(obj)
    obj["roof_quads"] = quads
    return obj, quads
