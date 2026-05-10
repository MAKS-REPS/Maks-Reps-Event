import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import math

# --- KONFIGURACJA ---
TOKEN = os.getenv('DISCORD_TOKEN') # Pobiera token ze zmiennych środowiskowych Railway
NAZWA_EVENTU = "Maks Reps Event"
PKT_PER_MSG = 2
COOLDOWN_MSG = 5

class MaksRepsBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)
        self.user_data = self.load_data()

    def load_data(self):
        if os.path.exists('data.json'):
            with open('data.json', 'r') as f:
                return json.load(f)
        return {}

    def save_data(self):
        with open('data.json', 'w') as f:
            json.dump(self.user_data, f, indent=4)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Zsynchronizowano komendy dla {NAZWA_EVENTU}")

bot = MaksRepsBot()

def get_level(points):
    lvl = math.floor(points / 100) + 1
    return min(lvl, 50)

@bot.tree.command(name="level", description="Sprawdź swój profil")
async def level(interaction: discord.Interaction):
    u_id = str(interaction.user.id)
    data = bot.user_data.get(u_id, {"points": 0, "msg_count": 0})
    
    pts = data["points"]
    lvl = get_level(pts)
    next_lvl_pts = lvl * 100
    
    # Obliczanie paska postępu
    progress_in_lvl = pts % 100
    bar_len = 10
    filled = int((progress_in_lvl / 100) * bar_len) if lvl < 50 else 10
    bar = "█" * filled + "░" * (bar_len - filled)
    
    embed = discord.Embed(title=f"Profil {interaction.user.display_name}", color=discord.Color.gold())
    embed.set_author(name=NAZWA_EVENTU)
    embed.add_field(name="Level", value=f"**{lvl}**", inline=True)
    embed.add_field(name="Punkty", value=f"**{pts}**", inline=True)
    embed.add_field(name="Postęp", value=f"[{bar}] {progress_in_lvl}/100 pkt", inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="daj_punkty", description="ADMIN: Dodaj punkty")
@app_commands.checks.has_permissions(administrator=True)
async def add_points(interaction: discord.Interaction, member: discord.Member, ilosc: int):
    u_id = str(member.id)
    if u_id not in bot.user_data:
        bot.user_data[u_id] = {"points": 0, "msg_count": 0}
    
    bot.user_data[u_id]["points"] += ilosc
    bot.save_data()
    await interaction.response.send_message(f"Dodano {ilosc} pkt dla {member.mention}!", ephemeral=True)

user_cooldowns = {}

@bot.event
async def on_message(message):
    if message.author.bot: return
    
    u_id = str(message.author.id)
    import time
    now = time.time()
    
    if now - user_cooldowns.get(u_id, 0) > COOLDOWN_MSG:
        if u_id not in bot.user_data:
            bot.user_data[u_id] = {"points": 0, "msg_count": 0}
        
        bot.user_data[u_id]["points"] += PKT_PER_MSG
        bot.user_data[u_id]["msg_count"] += 1
        user_cooldowns[u_id] = now
        bot.save_data() # Zapisujemy przy każdej wiadomości

bot.run(TOKEN)
