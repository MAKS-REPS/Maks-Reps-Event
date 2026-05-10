import discord
from discord.ext import commands
from discord import app_commands, ui
import asyncio
import random
from datetime import datetime, date

TICKET_CATEGORY_ID = 1486842150661656767
ALLOWED_CHANNELS = [1468529379318698117, 1457763945631715456]
KOLOR_BIALY = 0xffffff

# Tabela poziomów
LEVEL_DATA = {
    3: 275, 5: 500, 6: 750, 7: 1000, 9: 1666, 10: 2000, 
    12: 2600, 14: 3200, 15: 3500, 20: 6000, 50: 37500
}

def get_level_info(pts):
    lvl = 1
    for l, p in sorted(LEVEL_DATA.items()):
        if pts >= p: lvl = l
        else: break
    next_lvl = min([l for l in LEVEL_DATA.keys() if l > lvl] or [lvl])
    return lvl, next_lvl, LEVEL_DATA.get(next_lvl, pts)

class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    @app_commands.command(name="profil", description="Pokazuje twój profil eventowy")
    async def profil(self, interaction: discord.Interaction):
        d = self.bot.get_user(interaction.user.id)
        pts = d["points"]
        lvl, next_lvl, nxt_pts = get_level_info(pts)
        
        progress = min(int((pts / nxt_pts) * 100), 100)
        filled = progress // 10
        bar = "⬛" * filled + "⬜" * (10 - filled)

        sorted_users = sorted(self.bot.user_data.items(), key=lambda x: x[1].get('points', 0), reverse=True)
        rank = next((i for i, (uid, _) in enumerate(sorted_users, 1) if uid == str(interaction.user.id)), "N/A")

        embed = discord.Embed(color=KOLOR_BIALY)
        embed.set_author(name=f"Profil {interaction.user.name}")
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        embed.add_field(name="Level", value=f"**{lvl}**", inline=False)
        embed.add_field(name="Punkty", value=f"**{pts:.1f}**", inline=False)
        embed.add_field(name="Ranking", value=f"**#{rank}**", inline=False)
        embed.add_field(name="Wiadomości", value=f"**{d['msg_count']}**", inline=False)
        embed.add_field(name=f"Postęp do LVL {next_lvl}", value=f"[{bar}] **{progress}%**\n{pts:.1f} / {nxt_pts:.1f} pkt", inline=False)
        
        embed.set_footer(text=f"Maks Reps Event | Dziś o {datetime.now().strftime('%H:%M')}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="zadania", description="Lista wszystkich zadań")
    async def zadania(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Dostępne zadania", color=KOLOR_BIALY)
        tasks = [
            "1. **Rejestracja z linku**\nWIELORAZOWE | 80 pkt",
            "2. **Zaproszenie 2 osób na serwer**\nWIELORAZOWE | 100 pkt",
            "3. **Dodaj swojego haula na kanale**\nWIELORAZOWE | 50 - 200 pkt",
            "4. **Zgłoszenie błędu**\nWIELORAZOWE | 30 - 100 pkt",
            "5. **Podesłanie promki**\nWIELORAZOWE | 30 - 100 pkt",
            "6. **Zamówienie paki z mojego linku**\nWIELORAZOWE | 500 pkt",
            "7. **Boost serwera**\nJEDNORAZOWE | 150 pkt",
            "8. **Dodanie linku do discorda w bio**\nJEDNORAZOWE | 30 pkt",
            "9. **Zalogowanie na stronę**\nJEDNORAZOWE | 100 pkt",
            "10. **Obserwacja na tiktok**\nJEDNORAZOWE | 30 pkt",
            "11. **Obserwacja na instagramie**\nJEDNORAZOWE | 30 pkt"
        ]
        embed.description = "\n\n".join(tasks)
        embed.set_footer(text=f"Maks Reps Event | Dziś o {datetime.now().strftime('%H:%M')}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="odbierz", description="Zgłoś wykonanie zadania")
    async def odbierz(self, interaction: discord.Interaction):
        options = [
            discord.SelectOption(label="Paka z linku", value="PAKA", emoji="📦"),
            discord.SelectOption(label="Rejestracja", value="REJESTRACJA", emoji="🔗"),
            discord.SelectOption(label="Zaproszenia", value="ZAPROSZENIA", emoji="👥"),
            discord.SelectOption(label="Haul", value="HAUL", emoji="📹"),
            discord.SelectOption(label="Błąd", value="BŁĄD", emoji="⚠️"),
            discord.SelectOption(label="Promka", value="PROMKA", emoji="📢"),
            discord.SelectOption(label="Boost", value="BOOST", emoji="🚀"),
            discord.SelectOption(label="Bio", value="BIO", emoji="🌐"),
            discord.SelectOption(label="Strona", value="STRONA", emoji="💻"),
            discord.SelectOption(label="Sociale", value="SOCIALE", emoji="📱")
        ]

        class TicketView(ui.View):
            @ui.select(placeholder="Wybierz zadanie...", options=options)
            async def select_callback(self, inter, select):
                cat = inter.guild.get_channel(TICKET_CATEGORY_ID)
                ch = await inter.guild.create_text_channel(f"zgloszenie-{inter.user.name}", category=cat)
                
                emb = discord.Embed(color=KOLOR_BIALY, title="✨ NOWE ZGŁOSZENIE ✨")
                emb.description = f"Witaj {inter.user.mention}!\n\nWybrałeś kategorię: **{select.values[0]}**\n\n> Prosimy o podesłanie dowodu wykonania zadania.\n> Administracja zaraz Ci pomoże! 🛡️"
                emb.set_footer(text="Maks Reps System")
                
                await ch.send(f"{inter.user.mention} | @everyone", embed=emb)
                await inter.response.send_message(f"✅ Twój ticket został otwarty: {ch.mention}", ephemeral=True)

        await interaction.response.send_message("✨ **Wybierz zadanie, które wykonałeś:**", view=TicketView(), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Event(bot))
