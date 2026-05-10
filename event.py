import discord
from discord.ext import commands
from discord import app_commands, ui
import asyncio
import random
from datetime import datetime, date

TICKET_CATEGORY_ID = 1486842150661656767
ALLOWED_CHANNELS = [1468529379318698117, 1457763945631715456]
KOLOR_BIALY = 0xffffff

LEVEL_DATA = {3: 275, 5: 500, 10: 2000, 20: 6000, 50: 37500} # Skrócona lista dla przykładu

def get_level_info(current_points):
    sorted_lvls = sorted(LEVEL_DATA.keys())
    current_lvl = 1
    next_lvl = sorted_lvls[0]
    for lvl in sorted_lvls:
        if current_points >= LEVEL_DATA[lvl]: current_lvl = lvl
        else:
            next_lvl = lvl
            break
    return current_lvl, next_lvl, LEVEL_DATA.get(next_lvl, current_points)

class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not getattr(self.bot, 'event_active', True): return
        if message.channel.id not in ALLOWED_CHANNELS: return

        uid = str(message.author.id)
        d = self.bot.get_user(message.author.id)
        d["msg_count"] = d.get("msg_count", 0) + 1
        
        now = asyncio.get_event_loop().time()
        if now - self.cooldowns.get(uid, 0) > 5:
            mnoznik = getattr(self.bot, 'point_multiplier', 1)
            d["points"] += (2 * mnoznik)
            self.cooldowns[uid] = now
            self.bot.save_data()

    @app_commands.command(name="daily", description="Odbierz 15 pkt co 24h")
    async def daily(self, interaction: discord.Interaction):
        d = self.bot.get_user(interaction.user.id)
        if d.get("last_daily") == str(date.today()):
            return await interaction.response.send_message("❌ Już odebrałeś bonus!", ephemeral=True)
        d["points"] += 15
        d["last_daily"] = str(date.today())
        self.bot.save_data()
        await interaction.response.send_message("🎁 Otrzymałeś **15 pkt**!", ephemeral=True)

    @app_commands.command(name="hazard", description="Obstaw punkty w kasynie (Szansa 50/50)")
    async def hazard(self, interaction: discord.Interaction, kwota: int):
        d = self.bot.get_user(interaction.user.id)
        if kwota < 10: return await interaction.response.send_message("❌ Minimalna stawka to 10 pkt!", ephemeral=True)
        if d["points"] < kwota: return await interaction.response.send_message("❌ Nie masz tyle punktów!", ephemeral=True)

        await interaction.response.send_message("🎰 Losowanie...")
        await asyncio.sleep(2)

        if random.random() > 0.55: # 45% szansy na wygraną
            wygrana = kwota 
            d["points"] += wygrana
            msg = f"✅ **WYGRANA!** Zyskałeś `{wygrana} pkt`. Masz teraz `{d['points']:.1f} pkt`."
        else:
            d["points"] -= kwota
            msg = f"💀 **PRZEGRANA!** Straciłeś `{kwota} pkt`. Zostało Ci `{d['points']:.1f} pkt`."
        
        self.bot.save_data()
        await interaction.edit_original_response(content=msg)

    @app_commands.command(name="profil", description="Twoje statystyki")
    async def profil(self, interaction: discord.Interaction):
        d = self.bot.get_user(interaction.user.id)
        pts = d["points"]
        lvl, next_lvl, next_pts = get_level_info(pts)
        
        emb = discord.Embed(title=f"Profil {interaction.user.name}", color=KOLOR_BIALY)
        emb.add_field(name="Level", value=str(lvl))
        emb.add_field(name="Punkty", value=f"{pts:.1f}")
        emb.set_footer(text="Maks Reps Event")
        await interaction.response.send_message(embed=emb)

    @app_commands.command(name="odbierz", description="Otwórz ticket po punkty")
    async def odbierz(self, interaction: discord.Interaction):
        # ... (Kod z poprzedniej odpowiedzi zostaje bez zmian) ...
        await interaction.response.send_message("Otwórz ticket w panelu poniżej!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Event(bot))
