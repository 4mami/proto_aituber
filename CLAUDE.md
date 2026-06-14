# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 概要

`proto_aituber` — AITuber（AIで駆動するVTuber）のプロトタイプ。現時点でリポジトリに含まれるのは**開発環境のみ**で、アプリケーションコードはまだ追加されていない（`work/requirements.txt` は空で、`work/` も実質空）。新しいPythonコードは `work/` 配下に置く想定で、`work/` はコンテナ内の `/work` にバインドマウントされる。

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

- **ベースイメージ:** `pytorch/pytorch:2.12.0-cuda13.2-cudnn9-runtime`。GPUは compose の `deploy.resources` で予約しているため、ホストにNVIDIA Container Runtimeが必要。
- **ロケールは `ja_JP.UTF-8`** — このプロジェクトは日本語。コミットメッセージやコメントも日本語で書く。
- **ポート `8000`** がホスト↔コンテナで公開されており、今後アプリが立てるサーバー用を想定している。
- **永続化ボリューム:** `models` → Hugging Face hub のキャッシュ（`/root/.cache/huggingface/hub`）。ダウンロード済みモデルがコンテナ再ビルド後も残る。`claude` → Claude Code の設定。
- Claude Code はVS Code拡張に同梱されたものではなく、ネイティブインストーラ（`curl ... claude.ai/install.sh`）でイメージ内にインストールされている。設定は `claude` ボリューム + マウントした `~/.claude.json` により `down`/`up` をまたいで永続化される。
- **依存関係:** `work/requirements.txt` に追記する。ただしDockerfileの `pip install -r requirements.txt` 行は現在**コメントアウトされている**ため、再ビルドしても依存はインストールされない。手動でインストールする（`pip install -r requirements.txt --break-system-packages`）か、ファイルを記入したらこの行のコメントを外すこと。

### 実行 / デバッグ

- スクリプト実行: コンテナ内で `python work/<file>.py`。
- VS Codeデバッグ: 起動構成「Python デバッガー: 現在のファイル」が、開いているファイルを `justMyCode: false` で実行する。
- テストフレームワークやリンターはまだ未設定。Pyright/Pylance の型チェックは `standard`（`.vscode/settings.json`）。
