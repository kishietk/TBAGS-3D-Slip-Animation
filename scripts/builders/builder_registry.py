"""
ファイル名: builders/builder_registry.py

責務:
- SceneBuilder 用のビルダーレジストリを提供。
- コア要素の型と対応するビルダ関数をマッピングし、プラグイン的に拡張できるようにする。

使い方例:
    from builders.builder_registry import register_builder

    @register_builder(Beam)
    def build_beam(scene_builder, beam, ctx):
        # BeamBuilder の処理をここに実装
        ...

SceneBuilder 内では get_builder() で登録済み関数を取得し、
存在しなければデフォルト処理を呼び出す想定。

拡張:
- 必要に応じてビルダーの登録解除や全一覧の取得が可能。
"""

from typing import Type, Callable, Dict, Any, Optional
import logging

# コア要素の型 → ビルダ関数 のマッピング
BUILDER_REGISTRY: Dict[Type[Any], Callable[..., Any]] = {}


def register_builder(core_type: Type[Any]):
    """
    デコレータ: 指定した core_type（例：Beam, Column, Panel など）に
    対応するビルダ関数をレジストリに登録する。
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        BUILDER_REGISTRY[core_type] = fn
        return fn

    return decorator


def unregister_builder(core_type: Type[Any]):
    """
    core_type に対応するビルダ関数の登録を解除する。
    """
    if core_type in BUILDER_REGISTRY:
        BUILDER_REGISTRY.pop(core_type, None)


def get_builder(core_elem: Any) -> Optional[Callable[..., Any]]:
    """
    core_elem の型に対応するビルダ関数を返す。
    未登録の場合は None を返し、呼び出し側でフォールバック処理を行う想定。
    """
    elem_type = type(core_elem)
    print(f"Looking up builder for element type: {elem_type.__name__}")
    print(f"Current registry keys: {[cls.__name__ for cls in BUILDER_REGISTRY.keys()]}")
    return BUILDER_REGISTRY.get(elem_type)


def list_builders() -> Dict[Type[Any], Callable[..., Any]]:
    """
    現在登録されている全ビルダ関数の一覧を返す（デバッグ用途など）。
    """
    return dict(BUILDER_REGISTRY)


# -------------------------------------------------------------------
# プロジェクト内のビルダー群を強制的にインポートして登録処理を発火させる
try:
    import builders.object_builders.node_builder
    import builders.object_builders.column_builder
    import builders.object_builders.beam_builder
    import builders.object_builders.roof_builder
    import builders.object_builders.panel_builder
    import builders.object_builders.ground_builder
except ImportError as e:
    print(f"Error importing builder modules: {e}")
# -------------------------------------------------------------------
