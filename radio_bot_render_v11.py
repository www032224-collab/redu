import asyncio
from highrise import BaseBot, User
from highrise.models import SessionMetadata
from highrise.__main__ import main, BotDefinition

ROOM_ID = "695f30ddb10ff02e8ba0df4b"
TOKEN   = "007243ed44a910c0913006a6f206babde6d4dc1c2a68915d916a66b7f112f9fb"

class Bot(BaseBot):
    async def on_start(self, session_metadata: SessionMetadata):
        print("✅ البوت شغال!")
        await self.highrise.chat("🤖 مرحبا!")

    async def on_chat(self, user: User, message: str):
        if message == "ping":
            await self.highrise.chat("pong!")

asyncio.run(main([BotDefinition(Bot(), ROOM_ID, TOKEN)]))
