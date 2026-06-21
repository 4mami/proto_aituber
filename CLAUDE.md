# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 概要

`proto_aituber` — AITuber（AIで駆動するVTuber）のプロトタイプ。YouTube Liveのチャットを読み、ローカルLLMで応答を生成し、VOICEVOXで音声合成し、アバター（VTube Studio）を駆動して配信する。**Phase 1（コアパイプライン: チャット → LLM → TTS → 音声再生）が実装済み**で、全体構想とフェーズ計画は `docs/design.md` を参照。新しいPythonコードは `src/` 配下に置き、`src/` はコンテナ内の `/work` にバインドマウントされる。

主要コンポーネントの契約は `src/interfaces.py` の Protocol で定義される。**chat / llm / tts / audio** は本番実装と stub 実装（`src/<component>/stub.py`）の二重構成で、`src/main.py` の `--stub-*` フラグで差し替えできる。**avatar（`src/avatar/`）は Phase 3 以降の対象で、現状 stub・フラグともに未整備**（実行ループにも未統合）。Protocol 名・実装ファイル・利用可能なフラグの正確な一覧は、それぞれ `src/interfaces.py`・各 `src/<component>/`・`src/main.py` の引数定義を参照。

## 開発方針 — SDD ＋ ハーネスエンジニアリング

本リポジトリは **SDD（仕様駆動開発）＋ ハーネスエンジニアリング** の両輪で進める。

- **SDD（仕様駆動開発）:** `docs/design.md`（全体構想）を、フェーズ単位の**受け入れ条件付き仕様**へ落としてから実装する。仕様は `docs/specs/` 等に置き、`src/interfaces.py` の Protocol を「契約＝真実の源」として紐づける。新フェーズに着手する前に **要件 → 設計 → タスク分解** を書くこと。コードを直すより仕様を直す発想を優先する。
- **ハーネスエンジニアリング:** Protocol ＋ stub/本番の二重実装と `--stub-*` / `--stub-all` フラグを、**自動で回る検証ループ**（pytest スモークテスト＋Pyright型チェック）に接続する。受け入れ条件はそのまま stub 経由のテストケースにする。
- **当面の優先課題:** 検証ループが未整備（pytest・リンター未導入、CIなし）。`--stub-all` のスモークテストを起点に、ここの補強を最優先とする。
- **このファイルの保守方針:** 揮発性の事実（依存一覧・バージョンタグ・ポート番号・マウント先・設定値・フラグ名など、ファイルを見れば分かること）は散文に**書き写さず**、ソースファイルへの参照に留める（腐敗の面積を減らす）。記載するのは変わりにくい事実（アーキテクチャ・規約・なぜそうしたか）に絞る。インフラ/設定ファイルを編集したら本ファイルの該当箇所を見直すこと（`.claude/settings.json` のフックが編集時にリマインドする）。

## 開発環境

すべてはGPU対応のPyTorchコンテナ内で動作する。ホスト側でのPythonワークフローは存在しない。基本フローはVS Code Dev Container（`.devcontainer/devcontainer.json`、サービス `python`）、または `docker compose` の直接利用。

### 初回セットアップ

1. `.env.sample` から `.env` を作成する。3つの変数すべてが必須で、ホストとUID/GIDが一致する非rootのコンテナユーザーを作るために使われる（バインドマウントしたファイルの所有権を正しく保つため）:
   - `USERID`（ホストの `id -u`）、`GROUPID`（ホストの `id -g`）、`USERNAME`。
2. compose は `external` という名前の**外部** Dockerネットワークに接続する。事前に作成しておく必要がある:
   ```
   docker network create external
   ```
3. ビルドして起動:
   ```
   docker compose up -d --build
   docker compose exec python bash
   ```

### 環境の重要なポイント

- **ベースイメージ:** PyTorch公式のGPU対応イメージ（正確なタグは `docker/Dockerfile` の `FROM` を参照）。GPUは compose の `deploy.resources` で予約しているため、ホストにNVIDIA Container Runtimeが必要。
- **ロケールは `ja_JP.UTF-8`** — このプロジェクトは日本語。コミットメッセージやコメントも日本語で書く。
- **ポート公開:** 今後アプリが立てるサーバー用に、ホスト↔コンテナでポートを公開している（番号は `docker-compose.yml` の `ports` を参照）。
- **永続化ボリューム:** `models`（Hugging Face hub のキャッシュ。ダウンロード済みモデルが再ビルド後も残る）と `claude`（Claude Code の設定）。各マウント先は `docker-compose.yml` を参照。
- Claude Code はVS Code拡張に同梱されたものではなく、ネイティブインストーラ（`curl ... claude.ai/install.sh`）でイメージ内にインストールされている。設定は `claude` ボリューム + マウントした `~/.claude.json` により `down`/`up` をまたいで永続化される。
- **依存関係:** 一覧は `src/requirements.txt` を参照（ここに書き写さない）。Dockerfileの `pip install -r requirements.txt --break-system-packages` で**ビルド時にインストールされる**ため、依存を追加したら再ビルド（`docker compose up -d --build`）すれば反映される。コンテナ内で個別に追加する場合は `pip install <pkg> --break-system-packages`。
- **bitsandbytes の CUDA 13.2 対応:** インストールされる bitsandbytes が CUDA 13.2 向けバイナリを含まないため、Dockerfile内で近いCUDAバージョンの共有ライブラリへシンボリックリンクして代用している（具体的なバージョン・処理は `docker/Dockerfile` の該当ステップを参照）。

### 実行 / デバッグ

- スクリプト実行: コンテナ内で `python src/<file>.py`。
- VS Codeデバッグ: `.vscode/launch.json` の起動構成で、開いているファイルをそのまま実行できる（`justMyCode` 無効）。
- テストフレームワークやリンターはまだ未設定。型チェックは Pyright/Pylance（モードは `.vscode/settings.json` を参照）。
