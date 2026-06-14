# モデル・サービス設定
LLM_MODEL = "elyza/Llama-3-ELYZA-JP-8B"  # HF model ID またはローカルパス
LLM_LORA = None                            # LoRA adapter パス（不要なら None）
LLM_QUANTIZE = "4bit"                      # "4bit" / "8bit" / None

# キャラクター設定
CHARACTER_NAME = "あい"
SYSTEM_PROMPT = (
    f"あなたは「{CHARACTER_NAME}」という名前のVTuberです。"
    "明るく親しみやすい口調で視聴者のコメントに返答してください。"
    "返答は1〜2文の短い日本語でお願いします。"
)

# サービスURL
VOICEVOX_URL = "http://voicevox:50021"
VOICEVOX_SPEAKER = 3  # ずんだもん（ノーマル）

VTUBE_STUDIO_URL = "ws://localhost:8001"

YOUTUBE_LIVE_ID = ""  # YouTube Live の動画ID
