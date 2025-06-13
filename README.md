# TBAGS-Slip-Animation 構造可視化スクリプト

## 概要

本プロジェクトは**Blender**上で TBAGS 構造（免震サンドバッグ架構等）の  
**ノード・柱・梁・パネル・サンドバッグ・アニメーション**を一括生成・可視化するスクリプト群です。

- データ駆動・明確な責務分割・柔軟な拡張性
- 大規模・複雑モデルや特殊ラベルも容易に可視化
- 型ヒント・詳細 docstring とログ出力による透明性

---

## ディレクトリ構成

scripts/
├─ main.py # 実行エントリポイント（全パイプライン統括）
├─ configs/
│ ├─ constants.py # 物理定数・ID セット・描画用数値等
│ ├─ kind_labels.py # 部材種別 ID と分類・ラベル管理
│ └─ paths.py # データ/画像等ファイルパス集中管理
│
├─ cores/ # コア構造モデル（Node/Edge/Panel/Beam/Column/SandbagNode 等）
├─ builders/ # Blender オブジェクト生成（ノード球/サンドバッグ/柱/梁/パネル/屋根/ラベル/材料）
├─ loaders/ # データローダ（CSV/STR/アニメーション等）
├─ utils/ # 共通ユーティリティ（ロギング/Blender 初期化等）
├─ animators/ # アニメーション処理（建物・地面等のフレーム制御）
│
├─ data/ # 入出力データ（self.str, animation.csv 等）
├─ textures/ # 壁・屋根等の画像
└─ README.md # 本ファイル

---

## 動作要件

- **Blender 4.x 以降**（公式推奨）
- Python 3.10+（Blender 内蔵）
- mathutils, logging（Blender 標準同梱）
- 必須データ：
    data/
      animation-kumamoto-no-tbags.csv
      animation-kumamoto-with-tbags.csv
      kumamoto-erthquake-disp.csv
      self-no-tbags.str
      self-with-tbags.str
    textures/
      roof_texture.png
      wall_texture.png

---

## 使い方

### 1. データ準備

- `/data` ディレクトリに構造 STR やアニメーション CSV 等を格納
- `/textures` に壁・屋根等の画像テクスチャを配置

### 2. Blender スクリプト実行

Blender の「Scripting」タブで以下を実行

    import sys
    sys.path.insert(0, r"C:\Users\kishie\Documents\TBAGS-Slip-Animation\scripts")
    main_py = r"C:\Users\kishie\Documents\TBAGS-Slip-Animation\scripts\main.py"
    exec(compile(open(main_py, encoding="utf-8").read(), main_py, "exec"))

---

## 設計思想・特徴

- **集中管理と分割設計**

  - 定数・ラベル・ファイルパスは`configs/`ディレクトリで一元管理
  - コア層（Node/Edge/Panel）/Builder 層/Loader 層/Utility 層/Animator 層で明確に責務分割
  - サンドバッグ兼柱ノード等の特殊部材も、ID 集合・kind_id 分類で柔軟に管理

- **拡張容易性**

  - 定数・ID・ラベルを変更するだけで、新階層や特殊部材に容易対応
  - Builder/Animator 追加で新部材・機能も増強しやすい

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

---

## カスタマイズ・拡張ガイド

- **部材種別・ラベル・ID 追加**  
  → `configs/kind_labels.py`や`constants.py`を編集
- **マテリアルや見た目調整**  
  → `builders/materials.py`で色・質感を変更
- **アニメーション仕様の変更**  
  → `animators/`配下のアニメ制御ロジックを修正
- **Blender バージョン対応/拡張**  
  → Blender API 変更時は API ラッパ層や Service 追加で対応

---

## 開発・デバッグメモ

- 全関数・クラスに docstring ＋型ヒントあり
- デバッグ/進捗追跡は`utils/logging_utils.py`から全工程で可能
- ファイル読み込みエラー等は try/except ＋ログ記録で即時通知
- 設計・コーディングガイドは各モジュールの先頭コメントや`/docs/system.puml`（PlantUML 図）も参照

---

## 補足・参考

- システム設計可視化（PlantUML）は`/docs/system.puml`または下記参照
- 本 README・設計は 2025 年 6 月時点  
  ※新機能追加・構成変更時は随時アップデート推奨

---
