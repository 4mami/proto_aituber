import httpx


class VoicevoxClient:
    def __init__(self, base_url: str, speaker: int = 3):
        self._base_url = base_url.rstrip("/")
        self._speaker = speaker

    async def synthesize(self, text: str) -> bytes:
        async with httpx.AsyncClient(timeout=30.0) as client:
            query_resp = await client.post(
                f"{self._base_url}/audio_query",
                params={"text": text, "speaker": self._speaker},
            )
            query_resp.raise_for_status()

            wav_resp = await client.post(
                f"{self._base_url}/synthesis",
                params={"speaker": self._speaker},
                json=query_resp.json(),
            )
            wav_resp.raise_for_status()
            return wav_resp.content
