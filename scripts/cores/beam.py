# 梁（Beam）クラス
# Edgeクラスを継承し、梁であることを示す属性を追加する

from cores.edge import Edge


class Beam(Edge):
    """
    梁（Beam）のコアクラス
    Edgeクラスを継承し、is_beam属性を持つ
    """

    def __init__(self, *args, **kwargs):
        """
        Beamインスタンスを初期化する
        引数:
            *args: Edgeクラスの引数
            **kwargs: Edgeクラスのキーワード引数
        戻り値:
            なし
        """
        super().__init__(*args, **kwargs)
        self.is_beam = True
