"""
config.py

責務:
- configs/サブモジュールから必要な定数・設定をimportし、既存外部APIとの互換性を維持
- 既存コードの「from config import ...」や「import config」での利用をサポート

注意:
- 今後の設定追加・分割はconfigs/内で実施し、ここで集約する
"""

from configs.paths import *
from configs.constants import *
from configs.kind_labels import *
from configs.env import *
