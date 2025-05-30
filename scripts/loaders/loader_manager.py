from typing import Dict, List
from mathutils import Vector
from config import NODE_CSV, EDGES_FILE, ANIM_CSV
from loaders.node_loader import load_nodes
from loaders.edge_loader import load_edges_from_str
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

    def load_nodes(self) -> Dict[int, dict]:
        """
        ノードデータを辞書形式で返す。
        - key: ノードID
        - value: { 'pos': Vector, 'kind_id': int }
        """
        try:
            node_data_dict = load_nodes(self.node_path)
            result = {
                nid: {"pos": v.pos, "kind_id": v.kind_id}
                for nid, v in node_data_dict.items()
            }
            log.info(f"LoaderManager: Loaded {len(result)} nodes from {self.node_path}")
            return result
        except Exception as e:
            log.critical(f"LoaderManager: Failed to load nodes ({e})")
            raise

    def load_edges(self, node_map: Dict[int, dict]) -> List[dict]:
        """
        エッジデータをリスト形式で返す。
        - 各要素: { 'node_a': int, 'node_b': int, 'kind_id': int, 'kind_label': str }
        """
        try:
            # ダミーNodeインスタンスでload_edges_from_strを利用しても良いが、
            # 必要に応じてnode_mapをラップする形で適合させる
            from cores.node import Node

            temp_node_objs = {
                nid: Node(nid, data["pos"], kind_id=data["kind_id"])
                for nid, data in node_map.items()
            }
            edges = load_edges_from_str(self.edge_path, temp_node_objs)
            # 必要な情報だけ抽出
            result = []
            for e in edges:
                result.append(
                    {
                        "node_a": e.node_a.id,
                        "node_b": e.node_b.id,
                        "kind_id": getattr(e, "kind_id", None),
                        "kind_label": getattr(e, "kind_label", None),
                    }
                )
            log.info(f"LoaderManager: Loaded {len(result)} edges from {self.edge_path}")
            return result
        except Exception as e:
            log.critical(f"LoaderManager: Failed to load edges ({e})")
            raise

    def load_animation(self) -> Dict[int, Dict[int, "Vector"]]:
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
