from typing import Dict, List
from mathutils import Vector
from config import NODE_CSV, EDGES_FILE, ANIM_CSV
from loaders.node_loader import load_nodes, NodeData
from loaders.edge_loader import load_edges, EdgeData
from loaders.animation_loader import load_animation_data
from utils.logging_utils import setup_logging

log = setup_logging()


class LoaderManager:
    def __init__(
        self,
        node_path: str = NODE_CSV,
        edge_path: str = EDGES_FILE,
        anim_path: str = ANIM_CSV,
    ):
        self.node_path = node_path
        self.edge_path = edge_path
        self.anim_path = anim_path

    def load_nodes(self) -> Dict[int, NodeData]:
        """
        ノードデータ（NodeData型）の辞書を返す
        - key: ノードID
        - value: NodeData (NamedTuple: pos, kind_id)
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

    def load_edges(self, node_map: Dict[int, "NodeData"]) -> List["EdgeData"]:
        """
        エッジデータ（EdgeData型）のリストを返す
        - 各要素: EdgeData (NamedTuple: node_a, node_b, kind_id, kind_label)
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
        戻り値: {ノードID: {フレーム番号: Vector}}
        """
        try:
            anim_data = load_animation_data(self.anim_path)
            log.info(f"LoaderManager: Loaded animation data from {self.anim_path}")
            return anim_data
        except Exception as e:
            log.critical(f"LoaderManager: Failed to load animation ({e})")
            raise
