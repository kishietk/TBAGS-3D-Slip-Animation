"""
ファイル名: cores/parser_registry.py

責務:
- STRパーサーをモジュール単位で登録・管理するレジストリを提供。
- 各パーサー関数は、第一引数にテキスト行のイテレータ、戻り値として要素リストまたはNoneを返す仕様とする。

使い方:
    @register_parser
    def parse_beam(lines: Iterator[str]) -> Optional[List[EdgeData]]:
        ...

    def parse_structure_str(text: str):
        for fn in PARSER_REGISTRY:
            result = fn(lines_iter)
            if result is not None:
                return result

この仕組みで、新しいパーサーを追加する際はモジュール追加だけで済む。
"""

from typing import Callable, Iterator, Optional, List, Any

# パーサー関数のシグネチャ: linesイテレータを受け取り、パース成功時は結果リストを、そうでなければNoneを返す
ParserFunc = Callable[[Iterator[str]], Optional[List[Any]]]

# 登録済みパーサーのリスト
PARSER_REGISTRY: List[ParserFunc] = []


def register_parser(fn: ParserFunc) -> ParserFunc:
    """
    デコレータ: パーサー関数をレジストリに登録する。
    登録順が呼び出し優先順位になる。
    """
    PARSER_REGISTRY.append(fn)
    return fn


def unregister_parser(fn: ParserFunc) -> None:
    """
    指定したパーサー関数をレジストリから削除する。
    """
    try:
        PARSER_REGISTRY.remove(fn)
    except ValueError:
        pass


def clear_parsers() -> None:
    """
    全パーサー関数の登録を解除する（テスト用など）。
    """
    PARSER_REGISTRY.clear()


def list_parsers() -> List[ParserFunc]:
    """
    登録済みパーサー関数のリスト（コピー）を返す。
    """
    return list(PARSER_REGISTRY)
