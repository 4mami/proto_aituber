"""
AIVtuber メインループ

起動オプション:
  --stub-llm    LLMをスタブに切り替え（GPU不要）
  --stub-tts    TTSをスタブに切り替え（VOICEVOX不要）
  --stub-audio  音声再生をスタブに切り替え
  --stub-chat   チャットをキーボード入力に切り替え
  --stub-all    すべてスタブ（開発用）
"""
import asyncio
import argparse
import sys

import config


async def run(args: argparse.Namespace) -> None:
    use_stub_all = args.stub_all

    # --- Chat ---
    if use_stub_all or args.stub_chat:
        from chat.stub import StubChat
        chat = StubChat()
    else:
        from chat.youtube import YouTubeChat
        if not config.YOUTUBE_LIVE_ID:
            print("エラー: config.YOUTUBE_LIVE_ID が設定されていません。--stub-chat を使ってください。", file=sys.stderr)
            return
        chat = YouTubeChat(config.YOUTUBE_LIVE_ID)

    # --- LLM ---
    if use_stub_all or args.stub_llm:
        from llm.stub import StubLLM
        llm = StubLLM()
    else:
        from llm.hf_client import HFClient
        print(f"LLMをロード中: {config.LLM_MODEL} ...")
        llm = HFClient(config.LLM_MODEL, config.LLM_LORA, config.LLM_QUANTIZE)
        llm.load()
        print("LLMロード完了")

    # --- TTS ---
    if use_stub_all or args.stub_tts:
        from tts.stub import StubTTS
        tts = StubTTS()
    else:
        from tts.voicevox import VoicevoxClient
        tts = VoicevoxClient(config.VOICEVOX_URL, config.VOICEVOX_SPEAKER)

    # --- Audio ---
    if use_stub_all or args.stub_audio:
        from audio.stub import StubAudio
        audio = StubAudio()
    else:
        from audio.player import AudioPlayer
        audio = AudioPlayer()

    print("AIVtuber 起動しました。Ctrl+C で終了。")

    async for message in chat.messages():
        print(f"[チャット] {message.author}: {message.text}")

        try:
            response = await llm.generate(config.SYSTEM_PROMPT, message.text)
        except Exception as e:
            print(f"[LLMエラー] {e}", file=sys.stderr)
            continue

        print(f"[応答] {response}")

        try:
            wav = await tts.synthesize(response)
        except Exception as e:
            print(f"[TTSエラー] {e}", file=sys.stderr)
            continue

        try:
            await audio.play(wav)
        except Exception as e:
            print(f"[音声再生エラー] {e}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="AIVtuber")
    parser.add_argument("--stub-llm", action="store_true")
    parser.add_argument("--stub-tts", action="store_true")
    parser.add_argument("--stub-audio", action="store_true")
    parser.add_argument("--stub-chat", action="store_true")
    parser.add_argument("--stub-all", action="store_true")
    args = parser.parse_args()

    try:
        asyncio.run(run(args))
    except KeyboardInterrupt:
        print("\n終了しました。")


if __name__ == "__main__":
    main()
