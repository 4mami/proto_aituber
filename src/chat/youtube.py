import asyncio
import pytchat
from interfaces import ChatMessage


class YouTubeChat:
    def __init__(self, video_id: str):
        self._video_id = video_id

    async def messages(self):
        chat = pytchat.create(video_id=self._video_id)
        loop = asyncio.get_event_loop()
        while chat.is_alive():
            items = await loop.run_in_executor(None, lambda: list(chat.get().sync_items()))
            for item in items:
                yield ChatMessage(author=item.author.name, text=item.message)
            await asyncio.sleep(1.0)
