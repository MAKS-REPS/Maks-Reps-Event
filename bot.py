import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class GłównyBot(commands.Bot):
    def __init__(self):
        # Intents są WYMAGANE. Upewnij się, że włączyłeś je w Discord Developer Portal!
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        moduly = ['ai_expert', 'private_chat']
        for modul in moduly:
            try:
                await self.load_extension(modul)
                print(f"✅ Załadowano moduł: {modul}")
            except Exception as e:
                print(f"❌ BŁĄD ładowania modułu {modul}: {e}")

        # Wymuszamy synchronizację komend slash
        await self.tree.sync()
        print("✅ Komendy (Slash) zsynchronizowane!")

bot = GłównyBot()

@bot.event
async def on_ready():
    print(f"🚀 Bot gotowy i podłączony jako: {bot.user}")

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ Brak tokenu bota w Railway!")
