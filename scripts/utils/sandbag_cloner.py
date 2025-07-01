# """
# ファイル名: scripts/utils/sandbag_cloner.py

# 責務:
# - 代表サンドバッグオブジェクトを複製し、指定ノード位置に配置する
# - 複製先は CSV を再読み込みせず、代表のアニメーションデータを共有する
# """

# import bpy
# from utils import setup_logging
# from configs.constants import CLONE_POSITIONS, SANDBAG_OBJ_PREFIX
# from parsers.structure_parser import get_node_coords

# log = setup_logging("SandbagCloner")


# def clone_sandbags():
#     """
#     CLONE_POSITIONS に基づき、代表サンドバッグを複製・配置し、アニメーションを共有する。
#     前提:
#       - 代表は名前が SANDBAG_OBJ_PREFIX で始まり、'clone_' は含まない
#       - 代表にはカスタムプロパティ 'rep_node_id' が設定済み
#       - get_node_coords() が {node_id: Vector} マップを返す
#     """
#     node_coords = get_node_coords()

#     log.info("=== サンドバッグ複製処理 開始 ===")

#     # 1) 代表サンドバッグを収集
#     originals = [
#         obj
#         for obj in bpy.context.scene.objects
#         if obj.name.startswith(SANDBAG_OBJ_PREFIX)
#         and not obj.name.startswith(f"{SANDBAG_OBJ_PREFIX}clone_")
#     ]
#     log.info(f"検出した代表サンドバッグ数: {len(originals)}")

#     clone_total = 0

#     for orig in originals:
#         name = orig.name
#         log.info(f"処理中 → 代表サンドバッグ: '{name}'")

#         # rep_node_id の取得（代表ノードID）
#         rep_id = orig.get("rep_node_id")
#         if rep_id is None:
#             log.warning(f"'{name}' に 'rep_node_id' がありません。スキップします。")
#             continue
#         log.debug(f"→ rep_node_id={rep_id}")

#         # CLONE_POSITIONS から複製ノードリストを取得
#         clone_nodes = CLONE_POSITIONS.get(rep_id)
#         if not clone_nodes:
#             log.debug(
#                 f"CLONE_POSITIONS に rep_node_id={rep_id} の定義なし。スキップします。"
#             )
#             continue
#         log.info(f"→ 複製ノードIDリスト: {clone_nodes}")

#         # 2) 各複製ノードごとに処理
#         for node_id in clone_nodes:
#             log.info(f"ノードID {node_id} の座標取得…")
#             coord = node_coords.get(node_id)
#             if coord is None:
#                 log.warning(f"ノードID {node_id} の座標見つからず。スキップ。")
#                 continue
#             log.info(f"→ 座標: {coord}")

#             # オブジェクト複製
#             clone = orig.copy()
#             # メッシュデータ共有
#             if hasattr(orig, "data"):
#                 clone.data = orig.data

#             # 名前・位置設定
#             clone_name = f"{SANDBAG_OBJ_PREFIX}clone_{node_id}"
#             clone.name = clone_name
#             clone.location = coord
#             log.info(f"複製オブジェクト作成: {clone_name}")

#             # アニメーションデータ共有
#             log.info("アニメーションデータ共有処理開始…")
#             if orig.animation_data and orig.animation_data.action:
#                 clone.animation_data_clear()
#                 clone.animation_data_create()
#                 clone.animation_data.action = orig.animation_data.action
#                 log.info("→ アニメーションデータをコピーしました。")
#             else:
#                 log.info("→ 代表にアニメーションデータが存在しません。")

#             # コレクションへのリンク
#             if orig.users_collection:
#                 col = orig.users_collection[0]
#                 col.objects.link(clone)
#                 log.info(f"→ コレクション '{col.name}' にリンクしました。")
#             else:
#                 bpy.context.scene.collection.objects.link(clone)
#                 log.info("→ シーンコレクションにリンクしました。")

#             clone_total += 1

#     log.info(f"=== サンドバッグ複製処理 終了 === 合計クローン数: {clone_total} ===")
