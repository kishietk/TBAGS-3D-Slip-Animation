"""
プロジェクト全体で使用する全定数・設定値・パス管理モジュール

【設計方針・役割】
- すべての“マジックナンバー/マジックストリング”はここで一元管理
- 環境依存・パス・識別ID、特殊ノード種別（サンドバッグ/柱等）は明示的に型・コメント付与
- Blender外部環境依存が将来発生する場合は、.envやjson等で外部管理可能に拡張可
"""

import os
from mathutils import Vector
from typing import Set, Dict, List

# =======================
# 1. ディレクトリ・パス設定
# =======================

# プロジェクトルートディレクトリ（このファイルの場所基準）
PROJECT_DIR: str = os.path.dirname(os.path.abspath(__file__))

# データファイルディレクトリ
DATA_DIR: str = os.path.normpath(os.path.join(PROJECT_DIR, "../data"))
# テクスチャ画像ディレクトリ
TEXTURE_DIR: str = os.path.normpath(os.path.join(PROJECT_DIR, "../textures"))

# =======================
# 2. データファイルパス定義
# =======================

NODE_CSV: str = os.path.join(DATA_DIR, "self-with-tbags.str")
EDGES_FILE: str = os.path.join(DATA_DIR, "self-with-tbags.str")
NODE_ANIM_CSV: str = os.path.join(DATA_DIR, "animation-kumamoto-with-tbags.csv")
EARTHQUAKE_ANIM_CSV = os.path.join(DATA_DIR, "kumamoto-erthquake-disp.csv")


# =======================
# 3. 画像・テクスチャファイル
# =======================

WALL_IMG: str = os.path.join(TEXTURE_DIR, "wall_texture.png")
ROOF_IMG: str = os.path.join(TEXTURE_DIR, "roof_texture.png")

# =======================
# 4. ノードID・階層設定
# =======================

NODE_SECTION_NUMBERS: List[int] = list(range(1, 11))  # 1～10
NODE_IDS_2F: Set[int] = set(range(201, 209))
NODE_IDS_3F: Set[int] = set(range(301, 309))
NODE_IDS_4F: Set[int] = set(range(401, 409))
# kind_id=0は「サンドバッグ兼柱」専用ノード群として管理
NODE_IDS_SB1: Set[int] = {1143, 1148, 1153, 1158, 1243, 1248, 1253, 1258}
NODE_IDS_SB2: Set[int] = {3143, 3148, 3153, 3158, 3243, 3248, 3253, 3258}
NODE_IDS_SB3: Set[int] = {5143, 5148, 5153, 5158, 5243, 5248, 5253, 5258}
NODE_IDS_SB4: Set[int] = {11143, 11148, 11153, 11158, 11243, 11248, 11253, 11258}

NODE_IDS_SB5: Set[int] = {2354, 2359, 2366, 2372, 2379, 2385, 2391}
NODE_IDS_SB6: Set[int] = {4354, 4359, 4366, 4372, 4379, 4385, 4391}
NODE_IDS_SB7: Set[int] = {6354, 6359, 6366, 6372, 6379, 6385, 6391}
NODE_IDS_SB8: Set[int] = {12354, 12359, 12366, 12372, 12379, 12385, 12391}

VALID_NODE_IDS: Set[int] = (
    NODE_IDS_2F
    | NODE_IDS_3F
    | NODE_IDS_4F
    | NODE_IDS_SB1
    | NODE_IDS_SB2
    | NODE_IDS_SB3
    | NODE_IDS_SB4
    | NODE_IDS_SB5
    | NODE_IDS_SB6
    | NODE_IDS_SB7
    | NODE_IDS_SB8
)

# =========================
# 5. Blenderオブジェクト命名
# =========================

NODE_OBJ_PREFIX: str = "Node_"
PANEL_OBJ_PREFIX: str = "Panel_"
MEMBER_OBJ_PREFIX: str = "Member_"
COLUMN_OBJ_PREFIX: str = "Column_"
LABEL_OBJ_PREFIX: str = "Label_"
SANDBAG_OBJ_PREFIX: str = "Sandbag_"
ROOF_OBJ_NAME: str = "Roof"
ROOF_MESH_NAME: str = "RoofMesh"
UV_MAP_NAME: str = "UVMap"

# =========================
# 6. 幾何・数値パラメータ設定
# =========================

SPHERE_RADIUS: float = 0.24
MEMBER_THICK: float = 0.4
CYLINDER_VERTS: int = 8
EPS_XY_MATCH: float = 1e-3
EPS_AXIS: float = 1e-6
SANDBAG_CUBE_SIZE: Vector = Vector((3.0, 3.0, 0.05))

# =========================
# 7. ラベル・アニメーション設定
# =========================

LABEL_SIZE: float = 0.1
LABEL_OFFSET: Vector = Vector((0.8, -0.5, 0.5))
ANIM_FPS: int = 60
ANIM_SECONDS: int = 30
ANIM_TOTAL_FRAMES: int = ANIM_FPS * ANIM_SECONDS
DISP_SCALE: float = 10

# =========================
# 8. マテリアル透明度
# =========================

WALL_ALPHA: float = 0.8
ROOF_ALPHA: float = 0.6

# =========================
# 9. データCSV/STRヘッダー管理
# =========================

TYPE_HEADER: str = "(TYPE)"
CMP_HEADER: str = "(CMP)"
ID_HEADER: str = "(ID)"

# =========================
# 10. EBEAM3D部材種別管理
# =========================

EBEAM_KIND_LABELS: Dict[int, str] = {
    42: "frame_beam_x_and_y",
    43: "top_of_upper_level_sandbag_connecting_beam_y_direction",
    44: "bottom_of_upper_level_sandbag_connecting_beam_y_direction",
    45: "top_of_lower_sandbag_connecting_beam_y_direction",
    46: "bottom_of_lower_level_sandbag_connecting_beam_y_direction",
    47: "ground_connecting_elements_y_direction",
    48: "top_of_upper_level_sandbag_connecting_beams_x_direction",
    49: "bottom_of_upper_level_sandbag_connecting_beams_x_direction",
    50: "top_of_lower_level_sandbag_connecting_beams_x_direction",
    51: "bottom_of_lower_level_sandbag_connecting_beams_x_direction",
    52: "ground_connecting_elements_x_direction",
    53: "frame_column",
    54: "connecting_bottom_lower_level_sandbag_to_ground_with_foundation_on_top",
    55: "connecting_bottom_of_lower_level_sandbag_to_ground_without_foundation",
}
COLUMNS_KIND_IDS: List[int] = [53, 55]
BEAMS_KIND_IDS: List[int] = [42, 43, 44, 45, 46, 48, 49, 50, 51]
EDGE_NODE_KIND_IDS: List[int] = [0, 1]
WALL_NODE_KIND_IDS: List[int] = [0, 1]
SANDBAG_NODE_KIND_IDS: List[int] = [0, 2, 3, 4, 5, 7, 8, 9]

# =========================
# 11. ログ設定
# =========================

LOG_LEVEL: str = "INFO"
