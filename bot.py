import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class ElitarnyBotAI(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="!", 
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.watching, name="Maks Reps 👟 | /setup_ai_panel")
        )

    async def setup_hook(self):
        moduly = ['ai_expert', 'private_chat']
        for modul in moduly:
            try:
                await self.load_extension(modul)
                print(f"👑 [SYSTEM] Załadowano moduł premium: {modul}.py")
            except Exception as e:
                print(f"❌ [BŁĄD] Nie udało się załadować {modul}.py: {e}")

        await self.tree.sync()
        print("⚡ [SYSTEM] Wszystkie komendy Slash i przyciski zostały zsynchronizowane!")

bot = ElitarnyBotAI()

@bot.event
async def on_ready():
    print(f"✨ [SUKCES] Najlepszy Bot AI na świecie wystartował jako: {bot.user}")

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ [KRYTYCZNY BŁĄD] Brak DISCORD_TOKEN w zmiennych Railway!")
