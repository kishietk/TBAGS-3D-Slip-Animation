# core/parsers/registry.py

from typing import Dict
from .base import BaseParser

# Registry mapping file extension (without dot) to parser instance
_parser_map: Dict[str, BaseParser] = {}


def register_parser(ext: str, parser: BaseParser) -> None:
    """
    Register a parser instance for the given file extension.

    Args:
        ext (str): File extension (e.g. 'csv', 'str')
        parser (BaseParser): Parser instance to handle that extension
    """
    _parser_map[ext.lower()] = parser


def get_parser_for(path: str) -> BaseParser:
    """
    Retrieve the parser associated with the file extension of the given path.

    Args:
        path (str): Path to the file (must include extension)

    Returns:
        BaseParser: The parser instance registered for this extension

    Raises:
        ValueError: If no parser is registered for the file's extension
    """
    ext = path.lower().rsplit(".", 1)[-1]
    if ext not in _parser_map:
        raise ValueError(f"No parser registered for extension '{ext}'")
    return _parser_map[ext]
