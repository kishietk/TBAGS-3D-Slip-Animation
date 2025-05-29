# hotreload_utils.py
"""
モジュールのimport/reload（ホットリロード）ユーティリティ
"""

import importlib


def reload_modules(module_names: list, globals_dict: dict):
    """
    指定モジュールリストをimportまたはreload（Blender開発用ホットリロード向け）
    引数:
        module_names: strのリスト
        globals_dict: 呼び出し側のglobals()を渡す
    戻り値: なし
    """
    for m in module_names:
        try:
            if m in globals_dict:
                importlib.reload(globals_dict[m])
            else:
                globals_dict[m] = importlib.import_module(m)
        except Exception as e:
            print(f"[WARN] Failed to reload/import {m}: {e}")
