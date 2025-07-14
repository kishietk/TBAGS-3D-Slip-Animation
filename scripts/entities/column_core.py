"""
ファイル名: cores/columnCore.py

責務:
- Edgeクラスを継承した「柱（Column）」コアクラスを定義する。
- is_column属性を持ち、部材種判定やラベル出力等に用いる。

設計ポイント:
- ColumnはEdgeのサブクラス。is_column属性で型安全な分岐やラベル出力を実現。
"""

from .edge_core import Edge


class Column(Edge):
    """
    役割:
        Edgeクラスを継承した「柱（Column）」コアクラス。
        is_column属性を持ち、種別分岐やラベル出力等に利用。
    """

    def __init__(self, *args, **kwargs) -> None:
        """
        役割:
            Columnインスタンスを初期化（Edgeの初期化引数をそのまま利用）。
            is_column属性をTrueでセット。
        引数:
            *args: Edgeクラスの引数
            **kwargs: Edgeクラスのキーワード引数
        返り値:
            なし
        """
        super().__init__(*args, **kwargs)
        self.is_column: bool = True
