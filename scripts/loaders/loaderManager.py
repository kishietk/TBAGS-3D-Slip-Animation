"""
ファイル名: loaders/loaderManager.py

責務:
- ノード・エッジ・アニメーション全データの一元ロード管理クラス（LoaderManager）。
- 各データ種のロード専用関数を呼び出し、エラーハンドルやログも一括管理。

設計・運用指針:
- コンストラクタで各種パスを個別設定可能（デフォルトはconfig値）。
- 型ヒント・docstring統一で保守性向上。

TODO:
- ファイルが存在しない/パス間違い時のハンドリング（ユーザ向けガイドやリトライロジックの導入）
- 検証やテストのためfile-likeオブジェクト入力も選択可能なAPI拡張
"""

from typing import Dict, List
from mathutils import Vector
from configs import NODE_CSV, EDGES_FILE, NODE_ANIM_CSV
from loaders.nodeLoader import load_nodes, NodeData
from loaders.edgeLoader import load_edges, EdgeData
from loaders.nodeAnimLoader import load_animation_data
from utils.logging_utils import setup_logging

log = setup_logging("LoaderManager")


class LoaderManager:
    """
    役割:
        ノード・エッジ・アニメーションの全データを一括管理/ロードするクラス。
        パスの切り替えや一元的なログ出力も担う。

    属性:
        node_path (str): ノードCSVファイルパス
        edge_path (str): エッジ定義ファイルパス
        anim_path (str): アニメーションCSVファイルパス
    """

    def __init__(
        self,
        node_path: str = NODE_CSV,
        edge_path: str = EDGES_FILE,
        anim_path: str = NODE_ANIM_CSV,
    ):
        """
        役割:
            各データファイルパスを指定してインスタンス化する。
        引数:
            node_path (str): ノードファイルパス
            edge_path (str): エッジファイルパス
            anim_path (str): アニメーションファイルパス
        """
        self.node_path = node_path
        self.edge_path = edge_path
        self.anim_path = anim_path

    def load_nodes(self) -> Dict[int, NodeData]:
        """
        役割:
            ノードデータ（NodeData型）の辞書をロードして返す。
        返り値:
            Dict[int, NodeData]: ノードID→NodeData
        例外:
            Exception: 読込失敗時
        """
        try:
            node_data_dict = load_nodes(self.node_path)
            log.info(f"Loaded {len(node_data_dict)} nodes from {self.node_path}")
            return node_data_dict
        except Exception as e:
            log.critical(f"Failed to load nodes ({e})")
            raise

    def load_edges(self, node_map: Dict[int, NodeData]) -> List[EdgeData]:
        """
        役割:
            エッジデータ（EdgeData型）のリストをロードして返す。
        引数:
            node_map (Dict[int, NodeData]): ノードID→NodeDataの辞書
        返り値:
            List[EdgeData]: EdgeDataリスト
        例外:
            Exception: 読込失敗時
        """
        try:
            edges = load_edges(self.edge_path, node_map)
            log.info(f"Loaded {len(edges)} edges from {self.edge_path}")
            return edges
        except Exception as e:
            log.critical(f"Failed to load edges ({e})")
            raise

    def load_animation(self) -> Dict[int, Dict[int, Vector]]:
        """
        役割:
            アニメーションデータ（ノードIDごとの{フレーム: Vector}辞書）をロードして返す。
        返り値:
            Dict[int, Dict[int, Vector]]: {ノードID: {フレーム: Vector}}
        例外:
            Exception: 読込失敗時
        """
        try:
            anim_data = load_animation_data(self.anim_path)
            log.info(f"Loaded animation data from {self.anim_path}")
            return anim_data
        except Exception as e:
            log.critical(f"Failed to load animation ({e})")
            raise
