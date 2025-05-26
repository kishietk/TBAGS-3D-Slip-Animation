# 柱（Column）クラス
# Edgeクラスを継承し、柱であることを示す属性を追加する

from cores.edge import Edge


class Column(Edge):
    """
    柱（Column）のコアクラス
    Edgeクラスを継承し、is_column属性を持つ
    """

    def __init__(self, *args, **kwargs):
        """
        Columnインスタンスを初期化する
        引数:
            *args: Edgeクラスの引数
            **kwargs: Edgeクラスのキーワード引数
        戻り値:
            なし
        """
        super().__init__(*args, **kwargs)
        self.is_column = True
