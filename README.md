# TBAGS-Slip-Animation 構造可視化スクリプト

---

## 概要

本プロジェクトは**Blender**上で TBAGS 構造（免震サンドバッグ架構等）の  
**ノード・柱・梁・パネル・サンドバッグ・アニメーション**を一括生成・可視化するスクリプト群です。

---

## ディレクトリ構成

プロジェクトルート
├─ scripts/
│ ├─ main.py
│ ├─ animators/
│ ├─ builders/
│ ├─ configs/
│ ├─ cores/
│ ├─ loaders/
│ └─ utils/
│ └─ parsers/
├─ data/
└─ textures/

---

## 動作要件

- **Blender 4.x 以降**（公式推奨）
- Python 3.10+（Blender 内蔵）
- mathutils, logging（Blender 標準同梱）

- 必須データ：

  data/
    animation-kumamoto-no-tbags.csv
    animation-kumamoto-with-tbags.csv
    animation-kobe-with-tbags.csv
    kumamoto-erthquake-disp.csv
    kobe-erthquake-disp.csv
    self-no-tbags.str
    self-with-tbags.str
    sandbag_template_low.blend

  textures/
    roof_texture.png
    wall_texture.png
    tbags_texture.jpeg

---

## 使い方

### 1. データ準備

- `/data` ディレクトリに構造 STR やアニメーション CSV 等を格納
- `/textures` に壁・屋根等の画像テクスチャを配置

### 2. Blender の「Scripting」タブで以下を実行

import sys
import runpy

main_py = r"C:\Users\kishie\Documents\TBAGS-Slip-Animation\scripts\main.py"

# ================================

# データセット選択肢

# sys.argv = [main_py, "--dataset=kumamoto_with_tbags"]

# sys.argv = [main_py, "--dataset=kumamoto_no_tbags"]

# sys.argv = [main_py, "--dataset=kobe_with_tbags"]

# データセット選択肢(未設定)

# sys.argv = [main_py, "--dataset=tohoku_with_tbags"]

# sys.argv = [main_py, "--dataset=tohoku_no_tbags"]

# sys.argv = [main_py, "--dataset=kobe_no_tbags"]

# ================================

sys.argv = [main_py, "--dataset=kobe_with_tbags"]

runpy.run_path(main_py, run_name="**main**")

---

## 主な課題・今後の改善ポイント

> 今後の開発・保守性向上のため、以下の点を意識するとさらに発展します。

### 1. main_utils.py（統括ファサード）の肥大化

- 工程が一か所に集中し、関数や引数変更の波及リスク大
- → ファサードクラス分割、DI 設計の検討

### 2. Loader/Cores 間のデータ変換ルール未統一

- 加工/フィルタの責務が各層で重複、型や仕様変更が伝播しやすい
- → DTO（データ転送オブジェクト）・ファクトリ導入の検討

### 3. Builder/Animator の密結合

- sceneBuilder 等が複数 Builder/Animator を直接 import
- → I/F 抽象化や Plugin 設計を推奨

### 4. configs の分割・命名・参照の見直し

- 定数/分類/ラベル/パス等が横断的に参照され、更新時に迷いがち
- → より厳密な「分類単位」分割やトップ集約型設計への移行

### 5. Cores 層の双方向参照（Node/Edge/Panel）

- 循環参照やメモリリークリスク
- → 片方向参照または ID のみ保持し、必要時に検索する設計への進化

### 6. Blender API 依存の深さ

- builders/animators が Blender API を直参照し、バージョンアップ時に広範囲修正が必要
- → API ラッパー/Service 層追加、疎結合化の推奨

### 7. utils の肥大化リスク

- logging_utils, scene_utils 等の共通部品が肥大化しやすい
- → ドメイン単位で独立 Utility パッケージ分割

### 8. main.py のグローバル初期化

- マルチエントリポイントやバッチ処理時にグローバル状態管理が煩雑
- → CLI/GUI/API 等への多様な起動方法を設計
