import bpy
from logging_utils import setup_logging
from config import NODE_LABEL_SIZE, NODE_LABEL_OFFSET
from mathutils import Vector, Quaternion
from config import NODE_OBJ_PREFIX

log = setup_logging()


def clear_scene():
    """
    シーン内の全オブジェクトを削除し、完全クリア状態にする
    """
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def build_nodes(nodes: dict, radius: float, anim_data: dict = None):
    """
    ノード座標リストから球メッシュ（ノード球）をBlender上に生成する
    必要に応じてアニメーション（変位量）もキーフレームとして付与

    引数:
        nodes: {nid: Vector}  ノード座標辞書
        radius: float         球の半径
        anim_data: {nid: {frame: Vector(dx,dy,dz), ...}, ...} 変位データ

    戻り値:
        objs: {nid: Object}   作成したノード球オブジェクト辞書
    """
    objs = {}
    for nid, pos in nodes.items():
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=pos)
        o = bpy.context.object
        o.name = f"{NODE_OBJ_PREFIX}{nid}"
        objs[nid] = o

        # アニメーションデータがあれば、キーフレーム登録
        if anim_data and nid in anim_data:
            for frame, offset in anim_data[nid].items():
                o.location = pos + offset
                o.keyframe_insert(data_path="location", frame=frame)
    return objs


def create_node_labels(nodes: dict, radius: float):
    """
    各ノード球に対応するラベル（ノードID）をTextオブジェクトとして追加し、
    ノード球の子オブジェクトとする

    引数:
        nodes: {nid: Vector} ノード座標辞書
        radius: float        球の半径（未使用だがシグネチャ維持）

    備考:
        - ラベルはノード球から少し離した場所（NODE_LABEL_OFFSET）に設置
        - 文字サイズ・回転・整列も調整
    """
    from math import radians

    for nid, pos in nodes.items():
        node_name = f"{NODE_OBJ_PREFIX}{nid}"
        if node_name not in bpy.data.objects:
            continue
        node_obj = bpy.data.objects[node_name]

        # Blender Textオブジェクトでラベル追加
        bpy.ops.object.text_add()
        text_obj = bpy.context.object
        text_obj.name = f"Label_{nid}"
        text_obj.data.body = str(nid)
        text_obj.data.size = NODE_LABEL_SIZE
        text_obj.data.align_x = "CENTER"
        text_obj.data.align_y = "CENTER"
        # X方向に90度回転し、ラベルを見やすく
        text_obj.rotation_euler = (radians(90), 0, 0)

        # ノード球の子にする
        text_obj.parent = node_obj
        # 指定オフセット分だけノード球から離す
        text_obj.location = Vector(NODE_LABEL_OFFSET)
