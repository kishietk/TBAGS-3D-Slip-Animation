"""
柱（Column）コアクラス
- Edgeクラスを継承し、「柱」専用属性is_columnを付与
- 梁・柱共通ロジックでも型安全な判別が可能

【設計ポイント】
- Column: Edgeのサブクラス
- is_column属性は種別分岐やラベル出力で活躍
"""

from cores.edgeCore import Edge


class Column(Edge):
    """
    柱（Column）コアクラス
    - Edgeクラスを継承し、is_column属性で「柱」判別
    """

    def __init__(self, *args, **kwargs) -> None:
        """
        Columnインスタンス初期化
        Args:
            *args: Edgeクラスの引数
            **kwargs: Edgeクラスのキーワード引数
        Returns:
            None
        """
        super().__init__(*args, **kwargs)
        self.is_column: bool = True
