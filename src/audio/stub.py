class StubAudio:
    async def play(self, wav_bytes: bytes) -> None:
        print(f"[Audio stub] {len(wav_bytes)} bytes のWAVを再生（スキップ）")
