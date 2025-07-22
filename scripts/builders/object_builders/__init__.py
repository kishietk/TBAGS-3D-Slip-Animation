# builders/object_builders/__init__.py

# Node, Beam, Column, Panel, Roof, Ground 向けビルダーを全て import しておく
from .node_builder import build_node  # @register_builder(Node)
from .beam_builder import build_beam  # @register_builder(Edge)
from .column_builder import build_column  # @register_builder(Column)
from .panel_builder import build_panel  # @register_builder(Panel)
from .ground_builder import build_ground  # @register_builder(Ground)

# 屋根パネル向けロジックが別にあれば import してください
