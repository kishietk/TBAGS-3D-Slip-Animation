from utils.logging_utils import setup_logging
from utils.blenderScene_utils import duplicate_object_hierarchy

log = setup_logging("duplicate_sandbags_to_nodes")


def duplicate_sandbags_to_nodes(
    template_obj, node_ids, node_map, name_prefix="TBAGS_Node_"
):
    """
    代表サンドバッグEmptyを、指定ノード位置リスト(node_ids)に複製・配置。
    - 各ノードに同名で配置し、アニメーションも代表サンドバッグと同じにする。
    - node_map: {node_id: Nodeオブジェクト}
    """
    created_objs = []
    for node_id in node_ids:
        pos = getattr(node_map[node_id], "pos", None)
        if pos is None:
            continue
        new_name = f"{name_prefix}{node_id}"
        dup = duplicate_object_hierarchy(template_obj, location=pos, new_name=new_name)
        # アクション・アニメーション付与（同じActionをリンクまたはBakeする）
        if template_obj.animation_data and template_obj.animation_data.action:
            dup.animation_data_create()
            dup.animation_data.action = template_obj.animation_data.action
        created_objs.append(dup)
    return created_objs
