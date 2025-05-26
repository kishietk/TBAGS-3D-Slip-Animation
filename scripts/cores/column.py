from cores.edge import Edge


class Column(Edge):
    """
    柱（Column）のコアクラス
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_column = True
