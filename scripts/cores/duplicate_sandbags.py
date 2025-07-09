import os
import bpy
from mathutils import Vector
from typing import Tuple, List, Optional, Dict

from configs.paths import DATA_DIR, FILE_WITH_TBAGS
from configs.node_ids import COPY_SAND_BAG_NODE_IDS
from parsers.structure_parser import parse_str


def load_node_positions(str_path: str) -> Dict[int, Vector]:
    """
    STRファイルをパースして、ノードID→座標マップを返す。
    parse_str が COPY_SAND_BAG_NODE_IDS に含まれる
    prototype／target を含めてくれるように修正済み。
    """
    positions = parse_str(str_path)
    print(f"[DEBUG] Loaded {len(positions)} node positions from STR.")
    print(f"[DEBUG] Node IDs: {sorted(positions.keys())}")
    return positions


def find_prototype(
    proto_id: int,
) -> Tuple[Optional[bpy.types.Object], Optional[bpy.types.Object]]:
    """
    シーンからプロトタイプとなるサンドバッグ Empty と
    その子の Armature を探して返す。
    """
    prefix = f"Sandbag_{proto_id}_"
    empty_obj = None

    # Empty タイプから優先的に探す
    for obj in bpy.data.objects:
        if obj.type == "EMPTY" and obj.name.startswith(prefix):
            empty_obj = obj
            print(f"[DEBUG] Prototype empty found: {obj.name}")
            break

    # 見つからない場合は名前だけで探す
    if empty_obj is None:
        for obj in bpy.data.objects:
            if obj.name.startswith(prefix):
                empty_obj = obj
                print(f"[DEBUG] Prototype (non-EMPTY) found: {obj.name}")
                break

    armature_obj = None
    if empty_obj:
        for child in empty_obj.children:
            if child.type == "ARMATURE":
                armature_obj = child
                print(f"[DEBUG] Found armature under {empty_obj.name}: {child.name}")
                break

    if empty_obj is None:
        print(f"[WARN] Prototype not found for proto_id {proto_id}")
    return empty_obj, armature_obj


def duplicate_sandbag(
    proto_empty: bpy.types.Object,
    proto_armature: Optional[bpy.types.Object],
    target_pos: Vector,
) -> List[bpy.types.Object]:
    """
    Prototype をコピーし、指定座標に Empty + Armature + メッシュを配置する。
    """
    cloned_objs: List[bpy.types.Object] = []

    # Empty 複製
    new_empty = proto_empty.copy()
    new_empty.data = None
    bpy.context.collection.objects.link(new_empty)
    new_empty.location = target_pos
    cloned_objs.append(new_empty)
    print(f"[DEBUG] Created new empty: {new_empty.name} at {tuple(target_pos)}")

    # Armature 複製
    new_arm = None
    if proto_armature:
        new_arm = proto_armature.copy()
        if proto_armature.data:
            new_arm.data = proto_armature.data.copy()
        bpy.context.collection.objects.link(new_arm)
        new_arm.parent = new_empty
        cloned_objs.append(new_arm)
        print(f"[DEBUG] Cloned ARMATURE {proto_armature.name} → {new_arm.name}")
    else:
        print(f"[WARN] No armature under {proto_empty.name}, skipping armature clone.")

    # メッシュ複製（追加）
    for child in proto_empty.children:
        if child.type == "MESH":
            new_mesh = child.copy()
            if child.data:
                new_mesh.data = child.data.copy()
            bpy.context.collection.objects.link(new_mesh)
            new_mesh.parent = new_empty

            # Armatureモディファイアを適用
            if new_arm:
                mod = new_mesh.modifiers.new("Armature", "ARMATURE")
                mod.object = new_arm

            cloned_objs.append(new_mesh)
            print(f"[DEBUG] Cloned MESH {child.name} → {new_mesh.name}")

    return cloned_objs


def duplicate_sandbags():
    """
    COPY_SAND_BAG_NODE_IDS に従い、
    prototype → 各 target への複製を実行する。
    """
    print("[INFO] Start duplicating sandbags...")
    str_file = os.path.join(DATA_DIR, FILE_WITH_TBAGS)
    print(f"[DEBUG] Parsing STR file at: {str_file}")
    node_positions = load_node_positions(str_file)

    for proto_id, target_ids in COPY_SAND_BAG_NODE_IDS.items():
        print(f"[DEBUG] Processing prototype {proto_id} → targets {sorted(target_ids)}")
        empty_obj, arm_obj = find_prototype(proto_id)
        if empty_obj is None:
            print(f"[WARN] Skipping prototype {proto_id} (not found).")
            continue

        for tid in sorted(target_ids):
            pos = node_positions.get(tid)
            if pos is None:
                print(f"[WARN] Position for node {tid} not found, skipping.")
                continue

            print(f"[DEBUG] Duplicating {proto_id} → {tid} at {tuple(pos)}")
            clones = duplicate_sandbag(empty_obj, arm_obj, pos)
            print(f"[INFO] Duplicated {proto_id} → {tid}: {len(clones)} objects")

    print("[INFO] Sandbag duplication done.")


if __name__ == "__main__":
    duplicate_sandbags()
