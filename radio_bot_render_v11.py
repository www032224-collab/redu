import asyncio
import os
from highrise import BaseBot, User
from highrise.models import SessionMetadata
from highrise.__main__ import main, BotDefinition
from aiohttp import web

ROOM_ID = "695f30ddb10ff02e8ba0df4b"
TOKEN   = "007243ed44a910c0913006a6f206babde6d4dc1c2a68915d916a66b7f112f9fb"

class TestBot(BaseBot):

    async def on_start(self, session_metadata: SessionMetadata):
        print("✅ البوت اتصل بنجاح!")
        print(f"🆔 Bot ID: {session_metadata.user_id}")
        await self.highrise.chat("🤖 البوت شغال!")

    async def on_chat(self, user: User, message: str):
        print(f"💬 {user.username}: {message}")
        if message.lower() == "ping":
            await self.highrise.chat("pong! 🏓")

    async def on_user_join(self, user: User, position):
        print(f"➡️ دخل: {user.username}")
        await self.highrise.chat(f"أهلاً @{user.username}!")

    async def on_user_leave(self, user: User):
        print(f"⬅️ خرج: {user.username}")


async def _main():
    # HTTP Server لـ Render
    app = web.Application()
    app.router.add_get("/health", lambda r: web.Response(text="OK"))
    app.router.add_get("/",       lambda r: web.Response(text="Bot Running!"))
    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    await web.TCPSite(runner, "0.0.0.0", port).start()
    print(f"✅ HTTP على port {port}")

    # البوت
    backoff = 5
    while True:
        try:
            print("🔌 جاري الاتصال...")
            await main([BotDefinition(TestBot(), ROOM_ID, TOKEN)])
            backoff = 5
        except Exception as e:
            print(f"❌ خطأ: {e} — إعادة خلال {backoff}s")
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


if __name__ == "__main__":
    asyncio.run(_main())
