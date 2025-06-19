# builders/base.py
from abc import ABC, abstractmethod


class BuilderBase(ABC):
    """すべてのビルダーが継承する抽象クラス"""

    def pre_build(self):
        """共通の前処理（ログ初期化など）"""
        pass

    @abstractmethod
    def build(self):
        """各ビルダーが実装するコア処理"""
        pass

    def post_build(self, result):
        """共通の後処理（結果の検証やログ出力など）"""
        return result

    def run(self):
        self.pre_build()
        result = self.build()
        return self.post_build(result)
