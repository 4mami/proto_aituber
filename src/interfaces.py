from typing import Protocol, AsyncIterator


class ChatMessage:
    def __init__(self, author: str, text: str):
        self.author = author
        self.text = text

    def __repr__(self) -> str:
        return f"ChatMessage(author={self.author!r}, text={self.text!r})"


class ChatSource(Protocol):
    async def messages(self) -> AsyncIterator[ChatMessage]:
        ...


class LLMClient(Protocol):
    async def generate(self, system: str, user: str) -> str:
        ...


class TTSClient(Protocol):
    async def synthesize(self, text: str) -> bytes:
        """テキストをWAVバイト列に変換する"""
        ...


class AudioPlayer(Protocol):
    async def play(self, wav_bytes: bytes) -> None:
        ...


class AvatarClient(Protocol):
    async def on_speaking(self, text: str) -> None:
        ...
