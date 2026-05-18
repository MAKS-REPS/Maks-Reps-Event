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
            activity=discord.Activity(type=discord.ActivityType.watching, name="Maks Reps 👟")
        )

    async def setup_hook(self):
        # 🔥 Ładujemy wszystkie 3 kluczowe i bezbłędne moduły
        moduly = ['ai_expert', 'private_chat', 'rep_hub']
        
        print("⚙️ [SYSTEM] Ładowanie modułów bota...")
        for modul in moduly:
            try:
                await self.load_extension(modul)
                print(f"✅ Załadowano: {modul}.py")
            except Exception as e:
                print(f"❌ Błąd ładowania {modul}.py: {e}")

        print("⚡ Synchronizacja komend ze strukturą Discord API...")
        await self.tree.sync()

bot = ElitarnyBotAI()

@bot.event
async def on_ready():
    print(f"\n🚀 BOT URUCHOMIONY I ZSYNCHRONIZOWANY!")
    print(f"🤖 Zalogowano jako: {bot.user.name}\n")

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ Brak DISCORD_TOKEN w zmiennych środowiskowych!")
