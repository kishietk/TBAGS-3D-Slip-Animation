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

NODE_CSV: str = os.path.join(DATA_DIR, "input-with-tbags.str")
EDGES_FILE: str = os.path.join(DATA_DIR, "input-with-tbags.str")
ANIM_CSV: str = os.path.join(DATA_DIR, "animation-kumamoto-with-tbags.csv")

# =======================
# 3. 画像・テクスチャファイル・Blenderファイル
# =======================

WALL_IMG: str = os.path.join(TEXTURE_DIR, "rc_texture.jpg")
ROOF_IMG: str = os.path.join(TEXTURE_DIR, "rc_texture.jpg")
TBAGS_IMG: str = os.path.join(TEXTURE_DIR, "tbags_texture.jpeg")
TBAGS_model: str = os.path.join(DATA_DIR, "sandbag_template_low.blend")

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

NODE_IDS_SB5: Set[int] = {2353, 2359, 2366, 2372, 2379, 2385, 2392}
NODE_IDS_SB6: Set[int] = {4353, 4359, 4366, 4372, 4379, 4385, 4392}
NODE_IDS_SB7: Set[int] = {6353, 6359, 6366, 6372, 6379, 6385, 6392}
NODE_IDS_SB8: Set[int] = {12353, 12359, 12366, 12372, 12379, 12385, 12392}

NODE_IDS_SB1143: Set[int] = {1101, 1102, 1103, 1104, 1105,
                             1121, 1122, 1123, 1124, 1125,
                             1141, 1142, 1144, 1145,
                             1161, 1162, 1163, 1164, 1165,
                             1181, 1182, 1183, 1184, 1185}
NODE_IDS_SB1148: Set[int] = {1106, 1107, 1108, 1109, 1110,
                             1126, 1127, 1128, 1129, 1130,
                             1146, 1147, 1149, 1150,
                             1166, 1167, 1168, 1169, 1170,
                             1186, 1187, 1188, 1189, 1190}
NODE_IDS_SB1153: Set[int] = {1111, 1112, 1113, 1114, 1115,
                             1131, 1132, 1133, 1134, 1135,
                             1151, 1152, 1154, 1155,
                             1171, 1172, 1173, 1174, 1175,
                             1191, 1192, 1193, 1194, 1195}
NODE_IDS_SB1158: Set[int] = {1116, 1117, 1118, 1119, 1120,
                             1136, 1137, 1138, 1139, 1140,
                             1156, 1157, 1159, 1160,
                             1176, 1177, 1178, 1179, 1180,
                             1196, 1197, 1198, 1199, 1200}
NODE_IDS_SB1243: Set[int] = {1201, 1202, 1203, 1204, 1205,
                             1221, 1222, 1223, 1224, 1225,
                             1241, 1242, 1244, 1245,
                             1261, 1262, 1263, 1264, 1265,
                             1281, 1282, 1283, 1284, 1285}
NODE_IDS_SB1248: Set[int] = {1206, 1207, 1208, 1209, 1210,
                             1226, 1227, 1228, 1229, 1230,
                             1246, 1247, 1249, 1250,
                             1266, 1267, 1268, 1269, 1270,
                             1286, 1287, 1288, 1289, 1290}
NODE_IDS_SB1253: Set[int] = {1211, 1212, 1213, 1214, 1215,
                             1231, 1232, 1233, 1234, 1235,
                             1251, 1252, 1254, 1255,
                             1271, 1272, 1273, 1274, 1275,
                             1291, 1292, 1293, 1294, 1295}
NODE_IDS_SB1258: Set[int] = {1216, 1217, 1218, 1219, 1220,
                             1236, 1237, 1238, 1239, 1240,
                             1256, 1257, 1259, 1260,
                             1276, 1277, 1278, 1279, 1280,
                             1296, 1297, 1298, 1299, 1300}

NODE_IDS_SB5143: Set[int] = {5101, 5102, 5103, 5104, 5105,
                             5121, 5122, 5123, 5124, 5125,
                             5141, 5142, 5144, 5145,
                             5161, 5162, 5163, 5164, 5165,
                             5181, 5182, 5183, 5184, 5185}

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
# TBAGS下側のノード
FICTION_NODE_IDS: Set[int] = (
    NODE_IDS_SB2
    | NODE_IDS_SB4
    | NODE_IDS_SB6
    | NODE_IDS_SB8
)
# TBAGSコピー用のノード
COPY_NODE_IDS: Set[int] = (
    NODE_IDS_SB1143
    | NODE_IDS_SB5143
    # | NODE_IDS_SB1148
    # | NODE_IDS_SB1153
    # | NODE_IDS_SB1158
    # | NODE_IDS_SB1243
    # | NODE_IDS_SB1248
    # | NODE_IDS_SB1253
    # | NODE_IDS_SB1258
)

SB_GROUPS = {
    1143: NODE_IDS_SB1143, 
    # 1148: NODE_IDS_SB1148,
    # 1153: NODE_IDS_SB1153, 
    # 1158: NODE_IDS_SB1158,
    # 1243: NODE_IDS_SB1243, 
    # 1248: NODE_IDS_SB1248,
    # 1253: NODE_IDS_SB1253, 
    # 1258: NODE_IDS_SB1258,
    5153: NODE_IDS_SB5143
}

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
ANIM_FPS: int = 32
ANIM_SECONDS: int = 30
ANIM_TOTAL_FRAMES: int = ANIM_FPS * ANIM_SECONDS
DISP_SCALE: float = 1

# =========================
# 8. マテリアル透明度
# =========================

WALL_ALPHA: float = 0.8
ROOF_ALPHA: float = 0.6
TBAGS_ALPHA: float = 1.0

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
