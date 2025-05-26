from cores.edge import Edge


class Beam(Edge):
    """
    梁（Beam）のコアクラス
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_beam = True
