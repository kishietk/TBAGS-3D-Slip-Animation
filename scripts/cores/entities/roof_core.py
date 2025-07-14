"""
ファイル名: cores/roof_core.py

責務:
- Panelクラスを継承した屋根（Roof）コアクラスを定義する。
- is_roof属性を持ち、パネル種別判定やラベル付与に利用する。

設計ポイント:
- RoofはPanelのサブクラス
- is_roof属性は型判定や他用途にも活用
"""

from .panel_core import Panel


class Roof(Panel):
    """
    役割:
        Panelクラスを継承した屋根（Roof）コアクラス。
        is_roof属性をTrueでセットし、型判定やラベル付与等に利用する。
    """

    def __init__(self, *args, **kwargs) -> None:
        """
        役割:
            Roofインスタンスを初期化し、Panelと同様の引数を受け付ける。
            is_roof属性をTrueにセットする。
        """
        super().__init__(*args, **kwargs)
        self.is_roof: bool = True

    def __repr__(self) -> str:
        """
        役割:
            屋根パネル情報を可読文字列で返す。
        """
        return (
            f"Roof(id={self.id}, kind={self.kind}, floor={self.floor}, "
            f"nodes={[n.id for n in self.nodes]})"
        )
