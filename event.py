import discord
from discord.ext import commands
from discord import app_commands, ui
import math
import asyncio
from datetime import datetime

# Konfiguracja
TICKET_CATEGORY_ID = 1486842150661656767
NAZWA_EVENTU = "Maks Reps Event"
# Lista ID kanałów, na których można zdobywać punkty
ALLOWED_CHANNELS = [1468529379318698117, 1457763945631715456]

# Tabela poziomów (Punkty ze zdjęcia podzielone przez 2)
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
        if current_points >= LEVEL_DATA[lvl]:
            current_lvl = lvl
        else:
            next_lvl = lvl
            break
    points_needed = LEVEL_DATA.get(next_lvl, current_points)
    return current_lvl, next_lvl, points_needed

class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        # Sprawdzenie: czy to bot, czy event jest aktywny ORAZ czy kanał jest na liście dozwolonych
        if message.author.bot or not getattr(self.bot, 'event_active', True): 
            return
        
        # AKTUALIZACJA: Punkty naliczane TYLKO na wybranych kanałach
        if message.channel.id not in ALLOWED_CHANNELS:
            return

        uid = str(message.author.id)
        d = self.bot.get_user(message.author.id)
        d["msg_count"] = d.get("msg_count", 0) + 1
        
        now = asyncio.get_event_loop().time()
        if now - self.cooldowns.get(uid, 0) > 5:
            d["points"] = d.get("points", 0) + 2
            self.cooldowns[uid] = now
            self.bot.save_data()

    @app_commands.command(name="profil", description="Pokazuje statystyki twojego konta")
    async def profil(self, interaction: discord.Interaction):
        d = self.bot.get_user(interaction.user.id)
        pts = d.get("points", 0.0)
        msgs = d.get("msg_count", 0)
        lvl, next_lvl, next_pts = get_level_info(pts)
        
        prev_pts = LEVEL_DATA.get(lvl, 0) if lvl > 1 else 0
        progress_range = next_pts - prev_pts
        current_progress = pts - prev_pts
        percentage = min(max(int((current_progress / progress_range) * 100), 0), 100) if progress_range > 0 else 100
        
        filled = percentage // 10
        bar = "⬜" * filled + "⬛" * (10 - filled)
        sorted_ranking = sorted(self.bot.user_data.items(), key=lambda x: x[1].get('points', 0), reverse=True)
        ranking_pos = next((f"#{i}" for i, (uid, _) in enumerate(sorted_ranking, 1) if uid == str(interaction.user.id)), "N/A")

        embed = discord.Embed(color=0x2b2d31)
        embed.set_author(name=f"Profil {interaction.user.name}")
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="Level", value=f"{lvl}", inline=False)
        embed.add_field(name="Punkty", value=f"{pts:.1f}", inline=False)
        embed.add_field(name="Ranking", value=f"{ranking_pos}", inline=False)
        embed.add_field(name="Wiadomości", value=f"{msgs}", inline=False)
        embed.add_field(name=f"Postęp do LVL {next_lvl}", value=f"[{bar}] **{percentage}%**\n{pts:.1f} / {next_pts:.1f} pkt", inline=False)
        
        embed.set_footer(text=f"Maks Reps Event | Dziś o {datetime.now().strftime('%H:%M')}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="zadania", description="Lista wszystkich zadań")
    async def zadania(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Dostępne zadania", color=0x2b2d31)
        tasks = [
            ("📦 1. Zamówienie paki", "WIELORAZOWE | 500 pkt"),
            ("🔗 2. Rejestracja z linku", "WIELORAZOWE | 50 pkt"),
            ("👥 3. Zaproszenie 2 osób", "WIELORAZOWE | 100 pkt"),
            ("📹 4. Dodaj haula", "WIELORAZOWE | 50-200 pkt"),
            ("⚠️ 5. Zgłoszenie błędu", "WIELORAZOWE | 30-100 pkt"),
            ("📢 6. Podesłanie promki", "WIELORAZOWE | 30-100 pkt"),
            ("🚀 7. Boost serwera", "JEDNORAZOWE | 150 pkt"),
            ("🌐 8. DC w bio", "JEDNORAZOWE | 30 pkt"),
            ("📱 9. TikTok", "JEDNORAZOWE | 30 pkt"),
            ("📸 10. Instagram", "JEDNORAZOWE | 30 pkt")
        ]
        for n, v in tasks: embed.add_field(name=n, value=v, inline=False)
        embed.set_footer(text=f"Maks Reps Event | Dziś o {datetime.now().strftime('%H:%M')}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="odbierz", description="Zgłoś wykonanie zadania")
    async def odbierz(self, interaction: discord.Interaction):
        options = [
            discord.SelectOption(label="Zamówienie paki", value="PAKA", emoji="📦"),
            discord.SelectOption(label="Rejestracja z linku", value="REJESTRACJA", emoji="🔗"),
            discord.SelectOption(label="Zaproszenia", value="ZAPROSZENIA", emoji="👥"),
            discord.SelectOption(label="Dodanie haula", value="HAUL", emoji="📹"),
            discord.SelectOption(label="Zgłoszenie błędu", value="BŁĄD", emoji="⚠️"),
            discord.SelectOption(label="Podesłanie promki", value="PROMKA", emoji="📢"),
            discord.SelectOption(label="Boost serwera", value="BOOST", emoji="🚀"),
            discord.SelectOption(label="Link dc w bio", value="BIO", emoji="🌐"),
            discord.SelectOption(label="Obserwacja Sociali", value="SOCIALE", emoji="📱")
        ]
        
        class TicketView(ui.View):
            @ui.select(placeholder="Wybierz zadanie...", options=options)
            async def select_callback(self, inter, select):
                cat = inter.guild.get_channel(TICKET_CATEGORY_ID)
                ch = await inter.guild.create_text_channel(f"zgloszenie-{inter.user.name}", category=cat)
                
                emb = discord.Embed(color=0x3498db, title="🎫 MAKS REPS × TICKET")
                emb.description = f"Witaj {inter.user.mention}!\n\nWybrałeś kategorię: **{select.values[0]}**.\n\nZaraz ktoś z administracji Ci pomoże."
                emb.set_footer(text=f"Maks Reps Event | Dziś o {datetime.now().strftime('%H:%M')}")
                
                await ch.send(f"{inter.user.mention} | @everyone", embed=emb)
                await inter.response.send_message(f"Otwarto ticket: {ch.mention}", ephemeral=True)

        await interaction.response.send_message("Wybierz zadanie z listy poniżej:", view=TicketView(), ephemeral=True)

    @app_commands.command(name="ranking", description="Top 10 graczy eventu")
    async def ranking(self, interaction: discord.Interaction):
        sorted_users = sorted(self.bot.user_data.items(), key=lambda x: x[1].get('points', 0), reverse=True)[:10]
        desc = ""
        for i, (uid, data) in enumerate(sorted_users, 1):
            desc += f"**#{i}** <@{uid}> — **{data.get('points', 0):.1f} pkt**\n"
        
        embed = discord.Embed(title="Ranking TOP 10 eventu", description=desc if desc else "Brak danych.", color=0x2b2d31)
        embed.set_footer(text=f"Maks Reps Event | Dziś o {datetime.now().strftime('%H:%M')}")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Event(bot))
