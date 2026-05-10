import discord
from discord.ext import commands
from discord import app_commands, ui
import math
import asyncio
from datetime import datetime, timedelta

TICKET_CATEGORY_ID = 1486842150661656767
NAZWA_EVENTU = "Maks Reps Event"

class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    def get_user(self, uid):
        uid = str(uid)
        if uid not in self.bot.user_data:
            self.bot.user_data[uid] = {"points": 0.0, "msg_count": 0, "last_daily": None}
        return self.bot.user_data[uid]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not self.bot.event_active: return
        uid = str(message.author.id)
        now = asyncio.get_event_loop().time()
        if now - self.cooldowns.get(uid, 0) > 5:
            d = self.get_user(uid)
            d["points"] += 2
            self.cooldowns[uid] = now
            self.bot.save_data()

    @app_commands.command(name="dailybonus", description="Odbierz swoją codzienną dawkę punktów!")
    async def daily_bonus(self, interaction: discord.Interaction):
        d = self.get_user(interaction.user.id)
        now = datetime.now()
        
        # Sprawdzanie, czy użytkownik już odebrał bonus
        last_daily_str = d.get("last_daily")
        
        if last_daily_str:
            last_daily = datetime.fromisoformat(last_daily_str)
            if now < last_daily + timedelta(days=1):
                wait_time = (last_daily + timedelta(days=1)) - now
                hours, remainder = divmod(int(wait_time.total_seconds()), 3600)
                minutes, _ = divmod(remainder, 60)
                
                embed_error = discord.Embed(
                    title="⏳ Jeszcze nie teraz!",
                    description=f"Odebrałeś już dzisiejszy bonus. \nWróć za: **{hours}h {minutes}m**.",
                    color=discord.Color.red()
                )
                return await interaction.response.send_message(embed=embed_error, ephemeral=True)

        # Przyznawanie nagrody (np. losowo od 15 do 30 pkt)
        reward = random.randint(15, 30)
        d["points"] += reward
        d["last_daily"] = now.isoformat()
        self.bot.save_data()

        embed_success = discord.Embed(
            title="🎁 Daily Bonus Odebrany!",
            description=f"Dostałeś dzisiaj: **{reward} pkt**",
            color=discord.Color.green()
        )
        embed_success.add_field(name="Twoje punkty łącznie", value=f"**{d['points']:.1f} pkt**")
        embed_success.set_footer(text="Wróć jutro po więcej!")
        
        await interaction.response.send_message(embed=embed_success)

    @app_commands.command(name="level", description="Pokazuje twój profil")
    async def level(self, interaction: discord.Interaction):
        d = self.get_user(interaction.user.id)
        pts = d["points"]
        lvl = min(math.floor(pts / 100) + 1, 50)
        progress = int(pts % 100)
        
        embed = discord.Embed(title=f"Profil: {interaction.user.display_name}", color=0x2b2d31)
        embed.set_author(name=NAZWA_EVENTU)
        embed.add_field(name="✨ Poziom", value=f"**{lvl}**", inline=True)
        embed.add_field(name="💰 Punkty", value=f"**{pts:.1f}**", inline=True)
        
        bar_size = 10
        filled = int((progress / 100) * bar_size)
        bar = "🟩" * filled + "⬛" * (bar_size - filled)
        embed.add_field(name=f"Postęp do Levelu {lvl+1}", value=f"{bar} **{progress}%**", inline=False)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ranking", description="Top 10 osób w evencie")
    async def ranking(self, interaction: discord.Interaction):
        sorted_users = sorted(self.bot.user_data.items(), key=lambda x: x[1]['points'], reverse=True)[:10]
        embed = discord.Embed(title=f"🏆 Ranking - {NAZWA_EVENTU}", color=discord.Color.gold())
        description = ""
        for i, (uid, data) in enumerate(sorted_users, 1):
            description += f"**{i}.** <@{uid}> — `{data['points']:.1f} pkt` (Lvl {min(math.floor(data['points']/100)+1, 50)})\n"
        embed.description = description if description else "Brak danych."
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="odbierz", description="Otwórz ticket, aby odebrać punkty")
    async def odbierz(self, interaction: discord.Interaction):
        # ... (reszta kodu ticketów pozostaje bez zmian jak w poprzednim kroku)
        pass

import random # Pamiętaj o dodaniu tego na samej górze pliku!

async def setup(bot):
    await bot.add_cog(Event(bot))
