# TBAGS-3D-Slip-Animation スクリプト群

## 概要

本リポジトリは、Blender上で「ノード位置CSV＋エッジSTR＋変位CSV」を自動可視化・アニメ化するPythonスクリプト一式です。

## 設計方針
- **マジックナンバー撲滅**：全パラメータ・ファイルパス・定数はconfig.pyで集中管理
- **SOLID原則/可読性重視**：処理責任をビルダー/ローダー/アニメーター/マテリアル等で分離
- **型ヒント徹底**：Python型ヒントで静的解析・エディタ補完・将来の拡張も容易

## 使い方
1. config.py でファイルパス/パラメータを自身の環境に合わせて編集
2. Blender上で main.py を実行（標準Python3.9+必須）
3. Blenderシーン上に自動で構造モデル＆アニメーションが生成されます

## ファイル構成
- scripts/
    - main.py ... 全体制御
    - config.py ... 全定数・パス管理
    - loaders/ ... CSV/STRローダ
    - builders/ ... 各種ジオメトリ・ラベル生成
    - animator.py ... アニメーション処理
    - materials.py ... マテリアル一括適用
    - logging_utils.py ... 標準ロギング設定

## カスタマイズ方法
- 設定追加は config.py へ
- オブジェクト生成/アニメロジック改造は builders/animator へ
- 詳細は各ファイルの先頭設計コメントを参照

## 作者
- Takeuchi Construction Inc.
- 問い合わせ先: kishie@takeuchi-const.co.jp

