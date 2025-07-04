# utils/bone_name_resolver.py

"""
bone_name_resolver.py

役割:
    - Armatureオブジェクト内の「rep」「other」用ボーン名を柔軟に探し出し、PoseBoneを返却するユーティリティ。

使い方:
    from utils.bone_name_resolver import get_rep_and_other_bones
    pb_rep, pb_oth = get_rep_and_other_bones(arm_obj)
"""

import logging
import bpy
from typing import Tuple, List

log = logging.getLogger("bone_name_resolver")


def get_rep_and_other_bones(
    arm_obj: bpy.types.Object,
    rep_defaults: List[str] = None,
    oth_defaults: List[str] = None,
) -> Tuple[bpy.types.PoseBone, bpy.types.PoseBone]:
    """
    Armatureオブジェクトから「rep」「other」用のPoseBoneを返す。

    rep_defaults／oth_defaults の順に名前を探し、
    最初に見つかったものを rep／other とする。

    デフォルトでは:
      rep_defaults = ["top", "Bone_Rep"]
      oth_defaults = ["bottom", "Bone_Other"]

    もしそれでも見つからなければ、pose.bones から最初の2本を rep/other にする。
    1本しかなければ rep=other にフォールバック。

    Args:
        arm_obj: 対象のArmatureオブジェクト
        rep_defaults: rep候補名リスト (優先順)
        oth_defaults: other候補名リスト (優先順)

    Returns:
        (pb_rep, pb_oth): PoseBone オブジェクト
    """
    # デフォルト候補
    if rep_defaults is None:
        rep_defaults = ["top", "Bone_Rep"]
    if oth_defaults is None:
        oth_defaults = ["bottom", "Bone_Other"]

    bone_names = list(arm_obj.pose.bones.keys())

    # 候補リストから最初にマッチする名前を拾う
    def pick_name(candidates: List[str]) -> str:
        for name in candidates:
            if name in bone_names:
                return name
        return None

    rep_name = pick_name(rep_defaults)
    oth_name = pick_name(oth_defaults)

    # 見つからなければ pose.bones の先頭から補完
    if rep_name is None or oth_name is None:
        if len(bone_names) >= 2:
            if rep_name is None:
                rep_name = bone_names[0]
            if oth_name is None:
                oth_name = bone_names[1]
        elif len(bone_names) == 1:
            rep_name = oth_name = bone_names[0]
        else:
            raise RuntimeError(f"[{arm_obj.name}] ボーンが存在しません。")

        log.warning(
            f"[{arm_obj.name}] 標準候補にマッチせず、"
            f"{rep_name}/{oth_name} を使用します。"
        )

    # PoseBone オブジェクト取得
    try:
        pb_rep = arm_obj.pose.bones[rep_name]
        pb_oth = arm_obj.pose.bones[oth_name]
    except KeyError as e:
        raise RuntimeError(f"[{arm_obj.name}] ボーン取得失敗: {e}")

    return pb_rep, pb_oth
