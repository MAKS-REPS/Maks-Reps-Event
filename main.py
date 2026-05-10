import discord
from discord.ext import commands
import os
import json
import asyncio

# --- KONFIGURACJA ---
TOKEN = os.getenv('DISCORD_TOKEN')
DATA_FILE = 'data.json'

class MaksRepsBot(commands.Bot):
    def __init__(self):
        # Intents są potrzebne, aby bot widział wiadomości i użytkowników
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)
        
        # Ładowanie danych użytkowników
        self.user_data = self.load_data()
        self.event_active = True
        self.point_multiplier = 1

    def load_data(self):
        """Wczytuje punkty z pliku JSON"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Błąd podczas wczytywania danych: {e}")
                return {}
        return {}

    def save_data(self):
        """Zapisuje punkty do pliku JSON"""
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.user_data, f, indent=4)
        except Exception as e:
            print(f"Błąd podczas zapisywania danych: {e}")

    def get_user(self, user_id):
        """Pobiera dane użytkownika lub tworzy nowe jeśli nie istnieje"""
        uid = str(user_id)
        if uid not in self.user_data:
            self.user_data[uid] = {
                "points": 0.0, 
                "msg_count": 0, 
                "last_daily": ""
            }
        return self.user_data[uid]

    async def setup_hook(self):
        """To wykonuje się przy starcie bota - ładuje pliki i synchronizuje komendy"""
        print("--- Uruchamianie modułów ---")
        
        extensions = ['event', 'admin', 'kasyno']
        
        for ext in extensions:
            try:
                await self.load_extension(ext)
                print(f"✅ Załadowano moduł: {ext}")
            except Exception as e:
                print(f"❌ Nie udało się załadować {ext}: {e}")

        # Synchronizacja komend slash (/) z serwerem Discorda
        print("🔄 Synchronizowanie komend slash... (to może chwilę potrwać)")
        await self.tree.sync()
        print("🚀 Komendy zsynchronizowane i gotowe!")

    async def on_ready(self):
        print(f"--- BOT ONLINE ---")
        print(f"Zalogowano jako: {self.user.name}")
        print(f"ID: {self.user.id}")
        print("------------------")

# Uruchomienie bota
async def main():
    bot = MaksRepsBot()
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot wyłączony.")
