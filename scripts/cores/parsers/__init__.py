# parsers/__init__.py
from .base import BaseParser
from .registry import register_parser, get_parser_for
from .earthquake_anim import EarthquakeAnimParser
from .structure import StructureParser
from .node_anim import NodeAnimParser

__all__ = [
    "BaseParser",
    "register_parser",
    "get_parser_for",
    "EarthquakeAnimParser",
    "StructureParser",
    "NodeAnimParser",
    # Add other parsers as needed
]
