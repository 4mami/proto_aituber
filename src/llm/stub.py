class StubLLM:
    async def generate(self, system: str, user: str) -> str:
        return f"「{user}」へのお返事です！ありがとうございます！"
