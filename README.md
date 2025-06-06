# TBAGS-Slip-Animation 構造可視化スクリプト

## 概要

本プロジェクトは、**Blender**上でTBAGS構造モデル（サンドバッグ等を含む実験構造物）の**ノード・梁・柱・パネル・アニメーション**を一括生成・可視化するためのスクリプト群です。  
データ駆動設計・責務分離により、**大規模データ・多段階拡張**にも柔軟対応します。

- データ（座標・エッジ・アニメーション）はCSV/STRで管理
- 各種コアモデル/ビルダー/ユーティリティをモジュール分割
- 特殊ノード（サンドバッグ兼柱等）の設計思想も明示
- コード全体に型ヒント・詳細docstringを完備

---

## ディレクトリ構成

scripts/
│ main.py # エントリーポイント（可視化パイプライン一括実行）
│ config.py # 全定数・ID・パス集中管理
│
├─cores # コアデータ構造層（ノード・エッジ・パネルなど）
├─builders # Blenderオブジェクト生成（ノード球/サンドバッグ/柱/梁/パネル/屋根/ラベル/マテリアル）
├─loaders # データローダ（CSV/STR読取・データ加工）
├─utils # 補助ユーティリティ（ロギング/Blender初期化等）
├─animators # アニメーション処理（ハンドラ・コールバック）
│
├─data/ # 入出力データ（self.str, animation.csv等）
├─textures/ # 画像テクスチャ（壁・屋根など）
└─README.md # このファイル


---

## 動作要件

- Blender 3.x 以降（Python 3.10+）
- mathutils, logging（Blender標準環境内でOK）
- データファイル（`data/self.str`, `data/animation.csv` ほか）

---

## 使い方

### 1. データファイル配置

- ノード・エッジ・アニメーション等データは`/data`ディレクトリに格納してください。

### 2. Blenderでスクリプト実行

1. Blenderの「Scripting」タブで`main.py`を開く
2. 必要なら`config.py`でパスやIDセットを調整
3. **[Run Script]** ボタンを押すだけで一括可視化（ノード/柱/梁/壁/屋根/アニメ付き）

---

## 設計思想・特徴

- **全定数/ID/パス集中管理**：`config.py`で一元管理。  
  特殊ノード集合（例：サンドバッグ兼柱ノード）は明記され、拡張時もここを修正するだけで済みます。
- **型ヒント・docstring徹底**：全関数・クラスで型ヒント＆用途解説コメントを完備。
- **責務分離**：  
  - *コア層*（Node/Edge/Panel/Sandbag...）：データ構造と双方向リンク管理  
  - *ビルダー層*：Blenderオブジェクト生成（アニメーションは担当外）  
  - *ローダ層*：データファイルからコアデータ構築  
  - *ユーティリティ*：シーン消去、ロギング等  
  - *アニメーター*：毎フレームのBlenderオブジェクト追従・変形を自動管理
- **特殊ノード設計**：  
  - `NODE_IDS_SB1`などで*サンドバッグ兼柱*となる特殊ノード集合を定義  
  - `kind_id`==0や`SANDBAG_NODE_KIND_IDS`による種別フィルタで球体・立方体生成を統一制御
- **拡張容易**：新規階層/特殊部材/新ラベル追加も`config.py`と対応ビルダー修正のみで対応

---

## カスタマイズ・拡張例

- **パネルIDや部材種別を追加したい場合**  
  → `config.py`でID集合やラベルを編集
- **壁や梁のマテリアル・見た目を変えたい**  
  → `builders/materials.py`のマテリアル生成関数を修正
- **サンドバッグの表示サイズを変えたい**  
  → `config.py`の`SANDBAG_CUBE_SIZE`を編集

---

## 開発・デバッグメモ

- 各関数・クラスの役割や引数はソース内docstringで解説
- ログは`utils/logging_utils.py`から出力され、デバッグ容易
- 異常系はログ＋例外raiseにより即時検知可能
- ファイル読み込みエラー等は全てtry/exceptでカバー済
