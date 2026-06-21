import asyncio
from interfaces import ChatMessage


class StubChat:
    async def messages(self):
        loop = asyncio.get_event_loop()
        while True:
            try:
                text = await loop.run_in_executor(None, input, "コメント入力 > ")
            except EOFError:
                break
            if text.strip():
                yield ChatMessage(author="テストユーザー", text=text.strip())
