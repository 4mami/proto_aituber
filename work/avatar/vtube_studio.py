import asyncio
import json
import websockets


class VTubeStudioClient:
    def __init__(self, url: str):
        self._url = url
        self._ws = None

    async def connect(self) -> None:
        self._ws = await websockets.connect(self._url)

    async def on_speaking(self, text: str) -> None:
        if self._ws is None:
            return
        # 将来的にリップシンク・表情制御APIを呼ぶ
        pass

    async def close(self) -> None:
        if self._ws:
            await self._ws.close()
