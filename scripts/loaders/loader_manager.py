# loader/loader_manager.py

from typing import Tuple, Dict, Any, List
from utils import setup_logging
from cores.parsers import StructureParser, NodeAnimParser, EarthquakeAnimParser
from cores import NodeData, EdgeData

log = setup_logging("LoaderManager")


class LoaderManager:
    """
    各種ファイルパーサーを明示的に管理し、構造データ・ノードアニメーション・地震アニメーションを個別にロードするLoader。
    動的レジストリではなく、専用Parserインスタンスをメンバとして保持します。
    """

    def __init__(self) -> None:
        self._structure_parser = StructureParser()
        self._node_anim_parser = NodeAnimParser()
        self._earthquake_anim_parser = EarthquakeAnimParser()

    def load_structure(self, path: str) -> Tuple[Dict[int, NodeData], List[EdgeData]]:
        """
        .strファイルを構造データ（ノード・エッジ）として読み込む
        """
        try:
            return self._structure_parser.parse(path)
        except Exception as e:
            log.critical(f"Failed to load structure from {path}: {e}")
            raise

    def load_animation(self, path: str) -> Dict[int, Dict[int, Any]]:
        """
        ノードアニメーションCSVをパースして返す
        """
        try:
            return self._node_anim_parser.parse(path)
        except Exception as e:
            log.critical(f"Failed to load node animation from {path}: {e}")
            raise

    def load_earthquake_motion(self, path: str) -> Any:
        """
        地震基準面アニメーションCSVをパースして返す
        """
        try:
            return self._earthquake_anim_parser.parse(path)
        except Exception as e:
            log.critical(f"Failed to load earthquake motion from {path}: {e}")
            raise
