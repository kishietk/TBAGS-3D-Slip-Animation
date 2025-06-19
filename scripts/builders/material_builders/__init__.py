# builders/material_builders/__init__.py

from .material_applicator import MaterialApplicator


def apply_all_materials(
    node_objs, sandbag_objs, panel_objs, roof_obj, member_objs, ground_obj=None
):
    """
    旧 apply_all_materials と同一シグネチャのラッパー。
    """
    applicator = MaterialApplicator(
        node_objs, sandbag_objs, panel_objs, roof_obj, member_objs, ground_obj
    )
    applicator.build()
