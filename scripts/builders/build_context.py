# builders/build_context.py

from dataclasses import dataclass, field
import bpy
from typing import Any, Dict, Optional
from mathutils import Vector


@dataclass
class BuildContext:
    """
    SceneBuilder／Builder 間で共通の情報をまとめて渡すコンテキスト。
    これにより、メソッドシグネチャが build(self, ctx, elem) の 1 つだけになります。
    新たな情報が必要になった場合はフィールド追加で拡張できます。
    """

    scene: bpy.types.Scene  # 現在の Blender シーン
    positions: Dict[int, Vector]  # ノードID→座標マッピング
    core: Any  # CoreFactory が返すコアモデル（Node, Edge, Panel群）
    extra: Optional[Dict[str, Any]] = field(default_factory=dict)
    """
    ビルダーやシーン制御が拡張された場合に、追加情報を柔軟に受け渡せるための拡張用辞書。
    例: 'materials', 'custom_params', 'logger' など自由に投入可能。
    """
