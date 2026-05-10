import discord
from discord.ext import commands
import os
import json

# Konfiguracja
TOKEN = os.getenv('DISCORD_TOKEN') 
DATA_FILE = 'data.json'
ALLOWED_CATEGORY_ID = 1503079432339066963 

class MaksRepsBot(commands.Bot):
    def __init__(self):
        # Aktywujemy wszystkie wymagane intenty
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)
        
        # Wczytywanie bazy danych przy starcie
        self.user_data = self.load_data()
        
        # Zmienne systemowe
        self.event_active = True
        self.point_multiplier = 1  # Obsługa Happy Hour

    def load_data(self):
        """Wczytuje punkty z pliku JSON. Jeśli plik nie istnieje, tworzy pusty słownik."""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print("✅ Baza punktów została pomyślnie wczytana.")
                    return data
            except Exception as e:
                print(f"❌ Błąd podczas wczytywania bazy: {e}")
                return {}
        return {}

    def save_data(self):
        """Zapisuje aktualny stan punktów do pliku JSON (bezpieczeństwo danych)."""
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.user_data, f, indent=4)
        except Exception as e:
            print(f"❌ KRYTYCZNY BŁĄD ZAPISU: {e}")

    def get_user(self, user_id):
        """Pobiera dane użytkownika lub tworzy nowy profil, jeśli go nie ma."""
        uid = str(user_id)
        if uid not in self.user_data:
            self.user_data[uid] = {
                "points": 0.0, 
                "msg_count": 0, 
                "last_daily": "" # Przechowuje datę ostatniego odebrania bonusu
            }
        return self.user_data[uid]

    async def setup_hook(self):
        """Konfiguracja modułów i sprawdzanie uprawnień przed startem."""
        
        @self.tree.interaction_check
        async def check_category(interaction: discord.Interaction):
            """Blokada komend poza wyznaczoną kategorią."""
            if not interaction.channel.category or interaction.channel.category_id != ALLOWED_CATEGORY_ID:
                await interaction.response.send_message(
                    f"❌ Komendy eventowe działają tylko w kategorii <#{ALLOWED_CATEGORY_ID}>!", 
                    ephemeral=True
                )
                return False
            return True

        # Ładowanie modułów (rozszerzeń)
        try:
            await self.load_extension('event')
            await self.load_extension('admin')
            print("✅ Moduły event i admin zostały załadowane.")
        except Exception as e:
            print(f"❌ Błąd ładowania modułów: {e}")

        # Synchronizacja komend "/" (Slash Commands)
        await self.tree.sync()
        print(f"🚀 Maks Reps Event: Komendy zsynchronizowane.")

    async def on_ready(self):
        print(f"🤖 Zalogowano jako: {self.user.name} (ID: {self.user.id})")
        print(f"⚪ Wszystkie embedy ustawione na kolor biały.")
        print(f"📊 System gotowy do naliczania punktów.")

# Uruchomienie bota
if __name__ == "__main__":
    bot = MaksRepsBot()
    bot.run(TOKEN)
