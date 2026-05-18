import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = os.getenv('GUILD_ID')

class GłównyBot(commands.Bot):
    def __init__(self):
        # Intents.all() są wymagane, aby bot mógł prawidłowo czytać wiadomości i działać na serwerze
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # 🔗 Łącznik: Ładujemy TYLKO moduł odpowiedzialny za AI
        modul = 'ai_expert'
        
        try:
            await self.load_extension(modul)
            print(f"✅ Pomyślnie załadowano łącznik AI: {modul}.py")
        except Exception as e:
            print(f"❌ Błąd podczas ładowania modułu AI ({modul}.py): {e}")

        # Synchronizacja komend slash (jeśli podano GUILD_ID w .env, synchronizuje od razu na Twój serwer)
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            print(f"✅ Komenda slash /ai zsynchronizowana dla serwera: {GUILD_ID}")
        else:
            await self.tree.sync()
            print("✅ Komenda slash /ai zsynchronizowana globalnie.")

bot = GłównyBot()

@bot.event
async def on_ready():
    print(f"🚀 Bot AI uruchomiony stabilnie! Zalogowano jako {bot.user}")

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ Brak TOKENU bota! Sprawdź plik .env")
