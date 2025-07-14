# cores/entities/ground_core.py

from dataclasses import dataclass


@dataclass
class Ground:
    """
    Groundエンティティ。
    SceneBuilderのextrasループで地面を生成するためのマーカークラス。
    現在は属性を持たず、GroundBuilderがconfigsからサイズ・位置を取得します。

    Attributes:
        (なし)
    """

    pass
