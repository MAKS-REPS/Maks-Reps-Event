import discord
from discord.ext import commands
from discord import app_commands, ui
import math
import asyncio
from datetime import datetime, date

TICKET_CATEGORY_ID = 1486842150661656767
NAZWA_EVENTU = "Maks Reps Event"
ALLOWED_CHANNELS = [1468529379318698117, 1457763945631715456]
KOLOR_BIALY = 0xffffff

LEVEL_DATA = {
    3: 275, 5: 500, 6: 750, 7: 1000, 9: 1666.5, 10: 2000,
    12: 2600, 14: 3200, 15: 3500, 16: 3916.5, 17: 4333.5, 18: 4750,
    19: 5375, 20: 6000, 22: 7350, 24: 8925, 25: 9750, 27: 11500,
    28: 12475, 29: 13450, 32: 16600, 34: 18950, 35: 20150, 37: 22650,
    38: 23933.5, 39: 25216.5, 42: 29150, 43: 30475, 45: 33000,
    46: 33916.5, 47: 34833.5, 48: 35750, 49: 36625, 50: 37500
}

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
            # System mnożnika Happy Hour
            mnoznik = getattr(self.bot, 'point_multiplier', 1)
            d["points"] = d.get("points", 0) + (2 * mnoznik)
            self.cooldowns[uid] = now
            self.bot.save_data()

    @app_commands.command(name="daily", description="Odbierz darmowe punkty co 24h")
    async def daily(self, interaction: discord.Interaction):
        d = self.bot.get_user(interaction.user.id)
        today = str(date.today())

        if d.get("last_daily") == today:
            return await interaction.response.send_message("❌ Bonus odebrany! Wróć jutro.", ephemeral=True)

        d["points"] += 15 # Bonus daily
        d["last_daily"] = today
        self.bot.save_data()

        emb = discord.Embed(title="🎁 Daily Bonus", description=f"Otrzymałeś **15 pkt**!", color=KOLOR_BIALY)
        await interaction.response.send_message(embed=emb)

    @app_commands.command(name="profil", description="Pokazuje statystyki konta")
    async def profil(self, interaction: discord.Interaction):
        d = self.bot.get_user(interaction.user.id)
        pts = d.get("points", 0.0)
        lvl, next_lvl, next_pts = get_level_info(pts)
        
        prev_pts = LEVEL_DATA.get(lvl, 0) if lvl > 1 else 0
        prog = min(max(int(((pts - prev_pts) / (next_pts - prev_pts)) * 100), 0), 100) if next_pts > prev_pts else 100
        bar = "⬜" * (prog // 10) + "⬛" * (10 - (prog // 10))

        emb = discord.Embed(color=KOLOR_BIALY)
        emb.set_author(name=f"Profil {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        emb.add_field(name="Level", value=str(lvl), inline=True)
        emb.add_field(name="Punkty", value=f"{pts:.1f}", inline=True)
        emb.add_field(name=f"Postęp do LVL {next_lvl}", value=f"[{bar}] **{prog}%**\n{pts:.1f} / {next_pts:.1f} pkt", inline=False)
        emb.set_footer(text=f"{NAZWA_EVENTU} | {datetime.now().strftime('%H:%M')}")
        await interaction.response.send_message(embed=emb)

    @app_commands.command(name="zadania", description="Lista zadań")
    async def zadania(self, interaction: discord.Interaction):
        emb = discord.Embed(title="Dostępne zadania", color=KOLOR_BIALY)
        tasks = [
            ("📦 Zamówienie paki", "500 pkt (Wielorazowe)"),
            ("🔗 Rejestracja z linku", "50 pkt (Wielorazowe)"),
            ("👥 Zaproszenie 2 osób", "100 pkt (Wielorazowe)"),
            ("📹 Dodaj haula", "50-200 pkt"),
            ("🚀 Boost serwera", "150 pkt (Jednorazowe)")
        ]
        for n, v in tasks: emb.add_field(name=n, value=v, inline=False)
        await interaction.response.send_message(embed=emb)

    @app_commands.command(name="odbierz", description="Otwórz ticket")
    async def odbierz(self, interaction: discord.Interaction):
        options = [
            discord.SelectOption(label="Zamówienie paki", value="PAKA", emoji="📦"),
            discord.SelectOption(label="Rejestracja z linku", value="REJESTRACJA", emoji="🔗"),
            discord.SelectOption(label="Zaproszenia", value="ZAPROSZENIA", emoji="👥"),
            discord.SelectOption(label="Boost serwera", value="BOOST", emoji="🚀")
        ]
        
        class TicketView(ui.View):
            @ui.select(placeholder="Wybierz zadanie...", options=options)
            async def select_callback(self, inter, select):
                cat = inter.guild.get_channel(TICKET_CATEGORY_ID)
                ch = await inter.guild.create_text_channel(f"zgloszenie-{inter.user.name}", category=cat)
                emb = discord.Embed(color=KOLOR_BIALY, title="🎫 MAKS REPS × TICKET")
                emb.description = f"Witaj {inter.user.mention}!\n\nWybrałeś kategorię: **{select.values[0]}**.\n\nZaraz ktoś z administracji Ci pomoże."
                await ch.send(f"{inter.user.mention} | @everyone", embed=emb)
                await inter.response.send_message(f"Otwarto ticket: {ch.mention}", ephemeral=True)

        await interaction.response.send_message("Wybierz zadanie:", view=TicketView(), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Event(bot))
