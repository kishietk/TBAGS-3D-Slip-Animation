"""
LoaderManager
- ノード・エッジ・アニメーション全データの一元ロード管理クラス
- 各種データ取得（load_nodes/load_edges/load_animation）を統合的に提供

【設計・運用指針】
- コンストラクタ引数でパスを切替可能（デフォルトはconfig値）
- 内部で各専用ローダを呼び出し、エラーハンドル・ログ出力も統一
- 型ヒント・ドキュメント完備でメンテ容易
"""

from typing import Dict, List
from mathutils import Vector
from config import NODE_CSV, EDGES_FILE, ANIM_CSV
from loaders.nodeLoader import load_nodes, NodeData
from loaders.edgeLoader import load_edges, EdgeData
from loaders.animationLoader import load_animation_data
from utils.logging_utils import setup_logging

log = setup_logging()


class LoaderManager:
    """
    全ロード管理クラス
    - ノード・エッジ・アニメーションCSV/STR一括ロード・ログ付き
    - パス切替やリトライにも柔軟に対応
    """

    def __init__(
        self,
        node_path: str = NODE_CSV,
        edge_path: str = EDGES_FILE,
        anim_path: str = ANIM_CSV,
    ):
        """
        Args:
            node_path (str): ノードファイルパス
            edge_path (str): エッジファイルパス
            anim_path (str): アニメーションファイルパス
        """
        self.node_path = node_path
        self.edge_path = edge_path
        self.anim_path = anim_path

    def load_nodes(self) -> Dict[int, NodeData]:
        """
        ノードデータ（NodeData型）の辞書を返す
        Returns:
            Dict[int, NodeData]: ノードID→NodeData
        Raises:
            Exception: 読込失敗時
        """
        try:
            node_data_dict = load_nodes(self.node_path)
            log.info(
                f"LoaderManager: Loaded {len(node_data_dict)} nodes from {self.node_path}"
            )
            return node_data_dict
        except Exception as e:
            log.critical(f"LoaderManager: Failed to load nodes ({e})")
            raise

    def load_edges(self, node_map: Dict[int, NodeData]) -> List[EdgeData]:
        """
        エッジデータ（EdgeData型）のリストを返す
        Args:
            node_map (Dict[int, NodeData]): ノードID→NodeDataの辞書
        Returns:
            List[EdgeData]: EdgeDataリスト
        Raises:
            Exception: 読込失敗時
        """
        try:
            edges = load_edges(self.edge_path, node_map)
            log.info(f"LoaderManager: Loaded {len(edges)} edges from {self.edge_path}")
            return edges
        except Exception as e:
            log.critical(f"LoaderManager: Failed to load edges ({e})")
            raise

    def load_animation(self) -> Dict[int, Dict[int, Vector]]:
        """
        アニメーションデータをロード。
        Returns:
            Dict[int, Dict[int, Vector]]: {ノードID: {フレーム: Vector}}
        Raises:
            Exception: 読込失敗時
        """
        try:
            anim_data = load_animation_data(self.anim_path)
            log.info(f"LoaderManager: Loaded animation data from {self.anim_path}")
            return anim_data
        except Exception as e:
            log.critical(f"LoaderManager: Failed to load animation ({e})")
            raise
