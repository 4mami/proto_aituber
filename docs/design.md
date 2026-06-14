# AIVtuber 設計ドキュメント

## 概要

AIで駆動するVTuber（AIVtuber）のプロトタイプ。YouTube Liveのチャットコメントを読み取り、ローカルLLMで応答を生成し、日本語音声合成で喋るシステム。

---

## システムアーキテクチャ

```
[YouTube Live Chat]
        ↓  pytchat
[チャット読み込み]
        ↓
[LLM 応答生成]       ← HuggingFace Transformers + GPU
        ↓
[音声合成 TTS]       ← VOICEVOX (Docker)
        ↓
[音声出力]
        ↓
[アバター制御]       ← VTube Studio WebSocket API
        ↓
   OBS Studio → YouTube Live 配信
```

---

## 技術スタック

| 役割 | 技術 | 備考 |
|------|------|------|
| LLM | HuggingFace Transformers | GPU推論・LoRA adapter対応 |
| 量子化 | bitsandbytes | 4bit / 8bit |
| LoRA | peft | ファインチューニング済みモデル読み込み |
| TTS | VOICEVOX | Dockerコンテナ。将来的にStyle-Bert-VITS2へ移行可能 |
| チャット取得 | pytchat | YouTube Live Chatポーリング |
| アバター | VRM + VTube Studio | VRoid Hubのフリーモデルを使用予定 |
| 配信 | OBS Studio | ホスト側で動作 |

---

## LLM 設計方針

Ollamaは使用しない。`transformers` で HuggingFace Hub のモデルを直接ロードする。  
モデルIDを `config.py` で指定するだけで任意のモデル（ファインチューニング済み含む）に切り替え可能。

```python
# config.py の切り替え箇所
LLM_MODEL    = "elyza/Llama-3-ELYZA-JP-8B"  # HF model ID またはローカルパス
LLM_LORA     = None                           # LoRA adapter パス（不要なら None）
LLM_QUANTIZE = "4bit"                         # "4bit" / "8bit" / None
```

ダウンロード済みモデルは `models` ボリューム（`/root/.cache/huggingface/hub`）に保持され、コンテナ再ビルド後も残る。

---

## ファイル構造

```
work/
├── requirements.txt
├── config.py              # モデル名・キャラクター設定・各サービスURL
├── interfaces.py          # Protocol 定義（LLMClient / TTSClient / ChatSource 等）
├── main.py                # メインループ（パイプライン全体）
├── llm/
│   ├── __init__.py
│   ├── stub.py            # スタブ（固定応答を返す）
│   └── hf_client.py       # HuggingFace Transformers 実装
├── tts/
│   ├── __init__.py
│   ├── stub.py            # スタブ（テキストをprint）
│   └── voicevox.py        # VOICEVOX REST API クライアント
├── chat/
│   ├── __init__.py
│   ├── stub.py            # スタブ（キーボード入力）
│   └── youtube.py         # YouTube Live Chat（pytchat）
├── audio/
│   ├── __init__.py
│   ├── stub.py            # スタブ（何もしない）
│   └── player.py          # sounddevice による音声再生
└── avatar/
    ├── __init__.py
    └── vtube_studio.py    # VTube Studio WebSocket API クライアント
```

---

## Docker 構成の変更点

`docker-compose.yml` に VOICEVOX サービスを追加する。

```yaml
voicevox:
  image: voicevox/voicevox_engine:cpu-latest
  ports:
    - "50021:50021"
  networks:
    - external
```

LLMはOllamaコンテナ不要。既存の `python` サービスがGPUを使ってそのまま推論する。

---

## 追加する依存ライブラリ

```
# work/requirements.txt
transformers>=4.45
accelerate>=0.34
bitsandbytes>=0.43
peft>=0.12
pytchat>=0.6
sounddevice>=0.5
scipy>=1.14        # WAV書き出し用
httpx>=0.27        # VOICEVOX REST クライアント用
```

---

## 開発フェーズ

### Phase 1 — コアパイプライン
- VOICEVOX コンテナを docker-compose に追加
- `interfaces.py` に Protocol 定義
- `main.py` にパイプライン全体のループ（スタブで動作）
- LLM実装（HuggingFace Transformers）
- TTS実装（VOICEVOX）
- 音声再生実装（sounddevice）

**完了目標:** テキスト入力 → LLM応答 → 音声再生 が動く

### Phase 2 — YouTube チャット連携
- `chat/youtube.py` を pytchat で実装
- コメントのキュー管理・スパムフィルタリング

### Phase 3 — アバター連携
- VRoid Hub からフリーVRMモデルを選定
- VTube Studio の WebSocket API でリップシンク・表情制御

### Phase 4 — 配信仕上げ
- OBS との音声連携（仮想オーディオデバイス）
- 感情に応じた表情の自動切り替え
