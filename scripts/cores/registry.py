from typing import Type, Iterable, Dict, Any
import logging

# ------------------------------------------------------
# ロガー設定: INFO レベル以上のログを確実に表示
# ------------------------------------------------------
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# kind_id から Core クラスへのマッピング
CORE_REGISTRY: Dict[int, Type[Any]] = {}


def register_core(kind_ids: Iterable[int]):
    """
    Decorator to register a core element class for given kind_id(s).

    Usage:
        @register_core([1, 2, 3])
        class Beam(Edge):
            ...
    """

    def decorator(cls: Type[Any]) -> Type[Any]:
        for kid in kind_ids:
            if kid in CORE_REGISTRY:
                log.warning(
                    f"Overwriting existing core registration for kind_id {kid} with {cls.__name__}"
                )
            CORE_REGISTRY[kid] = cls
            log.info(f"Registered core class {cls.__name__} for kind_id {kid}")
        return cls

    return decorator


def unregister_core(kind_id: int) -> None:
    """
    Unregister a core class for a given kind_id.
    """
    if kind_id in CORE_REGISTRY:
        log.info(f"Unregistering core class for kind_id {kind_id}")
    CORE_REGISTRY.pop(kind_id, None)


def get_core_class(kind_id: int) -> Type[Any]:
    """
    Retrieve the registered core class for a given kind_id.
    Raises KeyError if not registered.
    """
    cls = CORE_REGISTRY.get(kind_id)
    if cls is None:
        log.error(f"No core class registered for kind_id {kind_id}")
        raise KeyError(f"No core class registered for kind_id {kind_id}")
    log.debug(f"Retrieved core class {cls.__name__} for kind_id {kind_id}")
    return cls


def list_core_classes() -> Dict[int, Type[Any]]:
    """
    Return a copy of the current kind_id → core class registry.
    """
    log.info(f"Listing core classes: {list(CORE_REGISTRY.keys())}")
    return dict(CORE_REGISTRY)


# ------------------------------------------------------
# 以下、登録デコレータを発火させるための明示的なモジュール読み込み
# cores/entities 配下のコアクラス定義をすべてインポート
# ------------------------------------------------------
import cores.entities.beam_core
import cores.entities.column_core
import cores.entities.edge_core
import cores.entities.ground_core
import cores.entities.node_core
import cores.entities.panel_core
import cores.entities.roof_core

# モジュール読み込み後の登録状況をログ出力
log.info(f"CORE_REGISTRY initialized with kind_ids: {sorted(CORE_REGISTRY.keys())}")
