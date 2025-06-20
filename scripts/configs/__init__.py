"""
config.py

責務:
- configs/サブモジュールから必要な定数・設定をimportし、既存外部APIとの互換性を維持
- 既存コードの「from config import ...」や「import config」での利用をサポート
"""

from configs.paths import *
from configs.constants import *
from configs.kind_labels import *
