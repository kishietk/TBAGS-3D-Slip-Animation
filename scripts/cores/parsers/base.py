# core/parsers/base.py

from abc import ABC, abstractmethod
from typing import Any


class BaseParser(ABC):
    """
    抽象パーサー基底クラス。
    ファイルパスを受け取り、ドメインモデル（構造化データ）を返すインタフェースを定義します。
    """

    @abstractmethod
    def parse(self, path: str) -> Any:
        """
        指定されたファイルを読み込み、パースしてドメインデータを返す。

        Args:
            path (str): パース対象のファイルパス

        Returns:
            Any: パース結果としてのドメインデータモデル
        """
        ...
