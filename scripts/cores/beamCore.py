"""
ファイル名: cores/beamCore.py

責務:
- Edgeクラスを継承した「梁（Beam）」コアクラスを定義する。
- is_beam属性を持ち、部材種判定やラベル付与に用いる。

設計ポイント:
- BeamはEdgeのサブクラス
- is_beam属性は型判定や他用途にも活用
"""

from cores.edgeCore import Edge


class Beam(Edge):
    """
    役割:
        Edgeクラスを継承した「梁（Beam）」コアクラス。
        is_beam属性を持ち、型判定やラベル付与等に利用する。
    """

    def __init__(self, *args, **kwargs) -> None:
        """
        役割:
            Beamインスタンスを初期化（Edgeの初期化引数をそのまま利用）。
            is_beam属性をTrueでセット。
        引数:
            *args: Edgeクラスの引数
            **kwargs: Edgeクラスのキーワード引数
        返り値:
            なし
        """
        super().__init__(*args, **kwargs)
        self.is_beam: bool = True
