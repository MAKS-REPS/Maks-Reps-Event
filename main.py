import discord
from discord.ext import commands
import os
import json

# UPEWNIJ SIĘ, ŻE MASZ TOKEN W ŚRODOWISKU LUB WPISZ GO TUTAJ
TOKEN = os.getenv('DISCORD_TOKEN') 
DATA_FILE = 'data.json'
ALLOWED_CATEGORY_ID = 1503079432339066963 

class MaksRepsBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)
        # WCZYTYWANIE PUNKTÓW Z PLIKU
        self.user_data = self.load_data()
        self.event_active = True

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print("✅ Dane użytkowników zostały pomyślnie wczytane.")
                    return data
            except Exception as e:
                print(f"❌ Błąd wczytywania pliku: {e}")
                return {}
        return {}

    def save_data(self):
        """Ta funkcja fizycznie zapisuje punkty do pliku data.json"""
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.user_data, f, indent=4)
        except Exception as e:
            print(f"❌ BŁĄD ZAPISU DANYCH: {e}")

    def get_user(self, user_id):
        uid = str(user_id)
        if uid not in self.user_data:
            self.user_data[uid] = {"points": 0.0, "msg_count": 0}
        return self.user_data[uid]

    async def setup_hook(self):
        # Blokada kategorii
        @self.tree.interaction_check
        async def check_category(interaction: discord.Interaction):
            if not interaction.channel.category or interaction.channel.category_id != ALLOWED_CATEGORY_ID:
                await interaction.response.send_message(
                    f"❌ Tego bota można używać tylko w kategorii <#{ALLOWED_CATEGORY_ID}>!", 
                    ephemeral=True
                )
                return False
            return True

        # Ładowanie modułów
        await self.load_extension('event')
        await self.load_extension('admin')
        await self.tree.sync()
        print("🚀 Maks Reps Event Online!")

bot = MaksRepsBot()

@bot.event
async def on_ready():
    print(f"🤖 Zalogowano jako {bot.user}")

bot.run(TOKEN)
