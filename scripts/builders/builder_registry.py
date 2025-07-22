from typing import Any, Callable, Dict, Optional, Type

# コア要素型とビルダ関数を紐付けるレジストリ
BUILDER_REGISTRY: Dict[Type[Any], Callable[..., Any]] = {}


def register_builder(
    *core_types: Type[Any],
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    複数のコア要素型に対してビルダ関数を登録するデコレータ。
    使用例:
        @register_builder(Beam, Column)
        def build_beam_or_column(scene_builder, beam_or_column, ctx):
            ...
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        # 各コア型に対してビルダ関数を登録
        for core_type in core_types:
            BUILDER_REGISTRY[core_type] = fn
        return fn

    return decorator


def get_builder(core_elem: Any) -> Optional[Callable[..., Any]]:
    """
    指定されたコア要素に対応するビルダ関数を取得する。
    1) type(core_elem) に完全一致するビルダを優先
    2) その後 isinstance によるマッチング（サブクラス対応）
    一致するビルダがなければ None を返す。
    """
    # 1) まず完全一致を探す
    exact_fn = BUILDER_REGISTRY.get(type(core_elem))
    if exact_fn:
        return exact_fn

    # 2) 次に isinstance チェックでサブクラス対応
    for core_type, fn in BUILDER_REGISTRY.items():
        if isinstance(core_elem, core_type):
            return fn

    return None

import builders.object_builders

