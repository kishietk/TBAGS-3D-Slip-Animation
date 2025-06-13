"""
ファイル名: builders/labels.py

責務:
- 任意Blenderオブジェクトにテキストラベルを追加するユーティリティ。
- 親子付けまたはChildOf制約で親に追従（位置・追従方式のみ責任範囲）。

TODO:
- テキストスタイル・カラー等の外部化（専用ラベルビルダーへ昇格も視野）
- アニメ・可視性制御・重なり回避等の責任は今後分割可能性あり
"""

import bpy
from mathutils import Vector
from utils.logging_utils import setup_logging

log = setup_logging("labels")


def create_label(
    obj: bpy.types.Object,
    text: str,
    abs_size: float,
    offset: Vector = Vector((0, 0, 0)),
    name_prefix: str = "Label",
    use_constraint: bool = True,
) -> bpy.types.Object:
    """
    役割:
        指定Blenderオブジェクトにテキストラベルを追加する。

    引数:
        obj (bpy.types.Object): 親オブジェクト
        text (str): ラベルテキスト
        abs_size (float): テキスト絶対サイズ（Blender単位）
        offset (Vector): 親基準での位置オフセット
        name_prefix (str): オブジェクト名プリフィクス
        use_constraint (bool): ChildOf制約で追従（True推奨）

    返り値:
        bpy.types.Object: 作成されたテキストラベルオブジェクト

    補足:
        use_constraint=Trueの場合はワールド位置固定、
        Falseの場合はparentでローカル追従。
    """
    from math import radians

    if not isinstance(offset, Vector):
        offset = Vector(offset)

    bpy.ops.object.text_add()
    text_obj = bpy.context.object
    text_obj.name = f"{name_prefix}_{obj.name}"
    text_obj.data.body = text
    text_obj.data.align_x = "CENTER"
    text_obj.data.align_y = "CENTER"
    text_obj.rotation_euler = (radians(90), 0, 0)
    text_obj.data.size = abs_size

    if use_constraint:
        con = text_obj.constraints.new(type="CHILD_OF")
        con.target = obj
        con.use_scale_x = False
        con.use_scale_y = False
        con.use_scale_z = False
        text_obj.location = offset
        bpy.context.view_layer.update()
        text_obj.matrix_world.translation = obj.matrix_world @ offset
    else:
        text_obj.parent = obj
        text_obj.location = offset

    return text_obj
