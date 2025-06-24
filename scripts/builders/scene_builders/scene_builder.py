# builders/scene_builders/scene_builder.py

"""
ファイル名: builders/scene_builders/scene_builder.py

責務:
    - コアモデル（Node/SandbagUnit/Panel…）から Blender 用表示オブジェクト群を一括生成
    - kind_id で通常ノード／サンドバッグノードを自動仕分けし、各 Builder クラスに委譲
    - 生成物（ノード球、サンドバッグ基点Empty、サンドバッグユニット、パネル、屋根、柱、梁、地面）を返却

TODO:
    - 入力nodesの型（dict or list）を統一し、型ヒント強化
    - SandbagBuilderの外部設定化（テンプレートパスやユニットキー名など）
    - パラメータ化: sandbag_face_size/bar_thicknessをコンフィグから参照
    - 処理セクションの関数分割（prepare, build_base, build_units, summary）による可読性向上
    - 単体テスト追加: ユニットマップ生成とBuilder実行の正常系/異常系検証

注意:
    - column_edges, beam_edges は Edge 情報を渡す
    - nodes 引数は内部でdict or listに統一されるが、将来的にTypedDict導入検討
"""
import bpy
from typing import Any, Dict, List, Tuple, Union, Optional
from utils.logging_utils import setup_logging
from builders.base import BuilderBase
from builders.object_builders import (
    NodeBuilder,
    SandbagBuilder,
    SandbagUnitsBuilder,
    PanelBuilder,
    RoofBuilder,
    ColumnBuilder,
    BeamBuilder,
    GroundBuilder,
)
from cores.constructors import make_sandbag_unit
from configs import (
    SANDBAG_NODE_KIND_IDS,
    SPHERE_RADIUS,
    SANDBAG_FACE_SIZE,
    SANDBAG_BAR_THICKNESS,
)
from builders.object_builders import duplicate_sandbags_to_nodes

log = setup_logging("SceneBuilder")


def prepare_sandbag_units(all_nodes: Dict[int, Any]) -> List[Dict[str, Any]]:
    """
    SandbagUnitペアから、代表ノード／もう一方のノード情報をまとめた辞書リストを生成

    Args:
        all_nodes: 全NodeオブジェクトID→インスタンスマップ
    Returns:
        List[Dict]: {unit_id, rep_node, other_node} を要素とするリスト
    """
    units = make_sandbag_unit(all_nodes)
    result: List[Dict[str, Any]] = []
    for unit in units:
        n1, n2 = sorted(unit.nodes, key=lambda n: n.kind_id)
        result.append(
            {
                "unit_id": unit.id,
                "rep_node": n1,
                "other_node": n2,
            }
        )
    return result


class SceneBuilder(BuilderBase):
    """
    Coreモデル→Blenderシーンオブジェクト統括ビルダー
    """

    def __init__(
        self,
        nodes: Union[Dict[int, Any], List[Any]],
        column_edges: List[Tuple[int, int]],
        beam_edges: List[Tuple[int, int]],
        panels: Optional[List[Any]] = None,
        sandbag_face_size: Tuple[float, float] = SANDBAG_FACE_SIZE,
        sandbag_bar_thickness: float = SANDBAG_BAR_THICKNESS,
        include_ground: bool = True,
    ):
        super().__init__()
        self.nodes_data = nodes
        self.column_edges = column_edges
        self.beam_edges = beam_edges
        self.panels_data = panels or []
        self.sandbag_face_size = sandbag_face_size
        self.sandbag_bar_thickness = sandbag_bar_thickness
        self.include_ground = include_ground

    def build(
        self,
    ) -> Tuple[
        Dict[int, Any],  # node_objs
        Dict[Any, Any],  # sandbag_base_objs
        List[Any],  # panel_objs
        Any,  # roof_obj
        List[Tuple[int, int, int, int]],  # roof_quads
        List[Tuple[Any, int, int]],  # member_objs
        Any,  # ground_obj
    ]:
        """
        全オブジェクト生成のエントリーポイント
        Returns:
            node_objs, sandbag_base_objs, panel_objs, roof_obj, roof_quads, member_objs, ground_obj
        """
        # ノード iterable に統一
        iterable = (
            self.nodes_data.values()
            if isinstance(self.nodes_data, dict)
            else self.nodes_data
        )

        # 通常／サンドバッグノードを分離
        normal_nodes: Dict[int, Any] = {}
        sandbag_nodes: Dict[int, Any] = {}
        for node in iterable:
            if getattr(node, "kind_id", None) in SANDBAG_NODE_KIND_IDS:
                sandbag_nodes[node.id] = node
            else:
                normal_nodes[node.id] = node

        # 1. 通常ノード球体生成
        node_objs = NodeBuilder(normal_nodes, radius=SPHERE_RADIUS).run()

        # 2. サンドバッグ基点生成
        cube_size = (
            self.sandbag_face_size[0],
            self.sandbag_face_size[1],
            self.sandbag_bar_thickness,
        )
        prepared = prepare_sandbag_units({**normal_nodes, **sandbag_nodes})
        sandbag_base_objs = SandbagBuilder(prepared, cube_size=cube_size).build()

        # 例：複製グループ定義（この部分は外部から渡しても良い）
        SB_GROUPS = {
            1143: [1148, 1153, 1158],  # 代表1143→他3つに複製
            # 他グループも追加可
        }
        # シーン上のSandbagUnit_代表IDオブジェクトを取得
        for rep_id, copy_ids in SB_GROUPS.items():
            template_obj = bpy.data.objects.get(f"SandbagUnit_{rep_id}")
            if template_obj is None:
                log.warning(f"代表サンドバッグ {rep_id} が見つかりません")
                continue
            # node_mapの定義が必要（node_id→Nodeオブジェクト）
            node_map = {n.id: n for n in normal_nodes.values()}
            # 代表追従サンドバッグの複製＆配置
            duplicate_sandbags_to_nodes(template_obj, copy_ids, node_map)
            # ↑↑ ここまで追加 ↑↑

        # 3. サンドバッグユニットCollection化
        units_map: Dict[Any, List[int]] = {
            info["unit_id"]: [info["rep_node"].id, info["other_node"].id]
            for info in prepared
        }
        sandbag_unit_objs = (
            SandbagUnitsBuilder(units_map, sandbag_base_objs).run() if units_map else {}
        )

        # 4. パネル生成
        panel_objs = PanelBuilder(self.panels_data).run() if self.panels_data else []

        # 5. 屋根生成
        positions = {n.id: n.pos for n in normal_nodes.values()}
        positions.update({n.id: n.pos for n in sandbag_nodes.values()})
        roof_obj, roof_quads = RoofBuilder(positions).run()

        # 6. 部材生成
        col_map = ColumnBuilder(positions, self.column_edges, thickness=0.5).run()
        beam_map = BeamBuilder(positions, self.beam_edges, thickness=0.5).run()
        member_objs = [
            (obj, int(key.split("_")[0]), int(key.split("_")[1]))
            for key, obj in {**col_map, **beam_map}.items()
        ]

        # 7. 地面生成
        ground_obj = GroundBuilder().run() if self.include_ground else None

        # サマリー出力
        summary = (
            f"SceneBuilder Summary: Nodes={len(node_objs)}, "
            f"SandbagEmpties={len(sandbag_base_objs)}, Units={len(sandbag_unit_objs)}, "
            f"Panels={len(panel_objs)}, RoofQuads={len(roof_quads)}, "
            f"Members={len(member_objs)}, Ground={'Yes' if ground_obj else 'No'}"
        )
        log.info(summary)

        return (
            node_objs,
            sandbag_base_objs,
            panel_objs,
            roof_obj,
            roof_quads,
            member_objs,
            ground_obj,
        )
