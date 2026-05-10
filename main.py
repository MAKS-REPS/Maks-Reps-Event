import discord
from discord.ext import commands
import os
import json

TOKEN = os.getenv('DISCORD_TOKEN')
DATA_FILE = 'data.json'
ALLOWED_CATEGORY_ID = 1503079432339066963  # ID dozwolonej kategorii

class MaksRepsBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)
        self.user_data = self.load_data()
        self.event_active = True

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: return {}
        return {}

    def save_data(self):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.user_data, f, indent=4)

    def get_user(self, user_id):
        uid = str(user_id)
        if uid not in self.user_data:
            self.user_data[uid] = {"points": 0.0, "msg_count": 0}
        return self.user_data[uid]

    async def setup_hook(self):
        # Globalna blokada kategorii dla komend slash
        @self.tree.interaction_check
        async def check_category(interaction: discord.Interaction):
            # Jeśli kanał nie ma kategorii lub ID się nie zgadza
            if not interaction.channel.category or interaction.channel.category_id != ALLOWED_CATEGORY_ID:
                await interaction.response.send_message(
                    f"❌ Tego bota można używać tylko w kategorii <#{ALLOWED_CATEGORY_ID}>!", 
                    ephemeral=True
                )
                return False
            return True

        # Ładowanie modułów (kasyno usunięte)
        await self.load_extension('event')
        await self.load_extension('admin')
        
        await self.tree.sync()
        print("Maks Reps Event Online!")
        print(f"Blokada kategorii {ALLOWED_CATEGORY_ID} aktywna.")

bot = MaksRepsBot()

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")

bot.run(TOKEN)
