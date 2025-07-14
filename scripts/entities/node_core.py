"""
責務:
- 構造グラフ上のノード（Node）コアデータクラスを定義。
- ノードID・座標・種別ID・階層属性のみを純粋に保持。
- グラフ構造やリンクの管理責任は外部に完全移譲。

設計指針:
- データ属性以外の機能・参照・相互リンク・add_edge/add_panelなどは持たない。
- 参照型・構造管理はCoreGraph等の外部クラスに委譲。
- 型ヒント厳格化・pydantic/dataclass化も将来検討。

TODO:
- サンドバッグノードはkind_id=0で通常ノードと統一運用。
- さらなる属性管理外部化・データクラス強化も検討。
"""

from typing import Optional
from mathutils import Vector


class Node:
    """
    役割:
        構造グラフ上のノード（接点）コアデータクラス。
        ノードID・座標・階層・種別IDのみを純粋に保持。

    属性:
        id (int): ノードID
        pos (Vector): 座標
        floor (Optional[str]): 階層属性
        kind_id (Optional[int]): ノード種別ID
    """

    def __init__(
        self,
        id: int,
        pos: Vector,
        floor: Optional[str] = None,
        kind_id: Optional[int] = None,
    ) -> None:
        self.id: int = id
        self.pos: Vector = pos
        self.floor: Optional[str] = floor
        self.kind_id: Optional[int] = kind_id

    def __repr__(self) -> str:
        """
        役割:
            ノードの主要属性を可読文字列で返す。
        返り値:
            str
        """
        return f"Node(id={self.id}, pos={tuple(self.pos)}, floor={self.floor}, kind_id={self.kind_id})"
