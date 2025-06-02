"""
梁（Beam）コアクラス
- Edgeクラスを継承し、「梁」専用属性is_beamを付与
- データモデル上、梁・柱などEdge系クラスで一元的に管理可能

【設計ポイント】
- Beam: Edgeのサブクラス（Python OOP流儀）
- is_beam属性は判定用（型判定やラベル付与に便利）
"""

from cores.edgeCore import Edge


class Beam(Edge):
    """
    梁（Beam）コアクラス
    - Edgeクラスを継承し、is_beam属性で「梁」判別
    """

    def __init__(self, *args, **kwargs) -> None:
        """
        Beamインスタンス初期化
        Args:
            *args: Edgeクラスの引数
            **kwargs: Edgeクラスのキーワード引数
        Returns:
            None
        """
        super().__init__(*args, **kwargs)
        self.is_beam: bool = True
