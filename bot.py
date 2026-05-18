import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Ładowanie zmiennych środowiskowych (.env / Railway Variables)
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class ElitarnyBotAI(commands.Bot):
    def __init__(self):
        # Włączamy wszystkie intencje (Intents.all) dla pełnej funkcjonalności bota
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="!", 
            intents=intents,
            activity=discord.Activity(
                type=discord.ActivityType.watching, 
                name="Maks Reps 👟 | /setup_hub"
            )
        )

    async def setup_hook(self):
        # Lista wszystkich modułów rozszerzeń bota (w tym nowy ultra-szybki rep_hub)
        moduly = ['ai_expert', 'private_chat', 'rep_hub']
        
        print("⚙️ [SYSTEM] Rozpoczynanie ładowania modułów premium...")
        for modul in moduly:
            try:
                await self.load_extension(modul)
                print(f"👑 [SYSTEM] Załadowano moduł: {modul}.py")
            except Exception as e:
                print(f"❌ [BŁĄD] Nie udało się załadować {modul}.py: {e}")

        # Synchronizacja komend Slash (tree.sync) na wszystkich serwerach
        print("⚡ [SYSTEM] Synchronizowanie komend Slash z Discord API...")
        try:
            await self.tree.sync()
            print("✅ [SYSTEM] Wszystkie komendy i przyciski zostały pomyślnie zsynchronizowane!")
        except Exception as e:
            print(f"❌ [BŁĄD SYNCHRONIZACJI] {e}")

bot = ElitarnyBotAI()

@bot.event
async def on_ready():
    print("\n==================================================")
    print(f"✨ [SUKCES] Najlepszy Bot AI na świecie działa!")
    print(f"🤖 Zalogowano jako: {bot.user.name} ({bot.user.id})")
    print("==================================================\n")

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ [KRYTYCZNY BŁĄD] Brak DISCORD_TOKEN w zmiennych środowiskowych Railway!")
