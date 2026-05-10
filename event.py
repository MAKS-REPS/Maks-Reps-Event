import discord
from discord.ext import commands
from discord import app_commands, ui
import math
import asyncio
from datetime import datetime, timedelta
import random

TICKET_CATEGORY_ID = 1486842150661656767

class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not self.bot.event_active: return
        uid = str(message.author.id)
        d = self.bot.get_user(message.author.id)
        
        # Zliczanie wszystkich wiadomości do profilu
        d["msg_count"] = d.get("msg_count", 0) + 1
        
        now = asyncio.get_event_loop().time()
        if now - self.cooldowns.get(uid, 0) > 5:
            d["points"] += 2
            self.cooldowns[uid] = now
            self.bot.save_data()

    @app_commands.command(name="profil", description="Profil gracza")
    async def profil(self, interaction: discord.Interaction):
        d = self.bot.get_user(interaction.user.id)
        pts = d["points"]
        lvl = min(math.floor(pts / 100) + 1, 50)
        msgs = d.get("msg_count", 0)
        
        embed = discord.Embed(title=f"Profil {interaction.user.name}", color=0x2b2d31)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="Level", value=f"**{lvl}**", inline=False)
        embed.add_field(name="Punkty / EXP", value=f"**{pts:.1f}**", inline=False)
        embed.add_field(name="Wiadomości", value=f"**{msgs}**", inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="zadania", description="Lista dostępnych zadań")
    async def zadania(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📋 Zadania Serwerowe", color=0x3498db)
        embed.add_field(name="1. Zamówienie od agenta z refa", value="Nagroda: **300 pkt**\n*(Screenshot zamówienia)*", inline=False)
        embed.add_field(name="2. Haul na TikToku/YT z linkiem do dc", value="Nagroda: **500 pkt**", inline=False)
        embed.add_field(name="3. Pomoc innej osobie na serwerze", value="Nagroda: **10/20 pkt**", inline=False)
        embed.add_field(name="4. Zamówienie paki", value="Nagroda: **500 pkt**", inline=False)
        embed.add_field(name="5. Bycie aktywnym na czacie", value="Nagroda: **Level x 1.5 pkt**", inline=False)
        embed.set_footer(text="Użyj /odbierz, aby wysłać dowód.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="odbierz", description="Otwórz ticket")
    async def odbierz(self, interaction: discord.Interaction):
        view = ui.View()
        select = ui.Select(placeholder="Wybierz zadanie...")
        select.add_option(label="Zakup u Agenta", value="Agent")
        select.add_option(label="Haul na TT / YT", value="Haul")
        select.add_option(label="Pomoc innej osobie", value="Pomoc")
        select.add_option(label="Zamówienie paki", value="Paka")
        select.add_option(label="Inne", value="Inne")
        
        async def callback(inter):
            cat = inter.guild.get_channel(TICKET_CATEGORY_ID)
            ch = await inter.guild.create_text_channel(f"ticket-{inter.user.name}", category=cat)
            await ch.send(f"{inter.user.mention} Wybrano zadanie: **{select.values[0]}**\nPrześlij tutaj dowód wykonania zadania.")
            await inter.response.send_message(f"Otwarto: {ch.mention}", ephemeral=True)
            
        select.callback = callback
        view.add_item(select)
        await interaction.response.send_message("Wybierz zadanie:", view=view, ephemeral=True)

    @app_commands.command(name="dailybonus", description="Odbierz codzienną dawkę punktów")
    async def daily_bonus(self, interaction: discord.Interaction):
        d = self.bot.get_user(interaction.user.id)
        now = datetime.now()
        last_daily_str = d.get("last_daily")
        
        if last_daily_str:
            last_daily = datetime.fromisoformat(last_daily_str)
            if now < last_daily + timedelta(days=1):
                wait_time = (last_daily + timedelta(days=1)) - now
                hours, remainder = divmod(int(wait_time.total_seconds()), 3600)
                minutes, _ = divmod(remainder, 60)
                embed_error = discord.Embed(
                    title="⏳ Jeszcze nie teraz!",
                    description=f"Wróć za: **{hours}h {minutes}m**.",
                    color=discord.Color.red()
                )
                return await interaction.response.send_message(embed=embed_error, ephemeral=True)

        reward = random.randint(15, 30)
        d["points"] += reward
        d["last_daily"] = now.isoformat()
        self.bot.save_data()

        embed_success = discord.Embed(
            title="🎁 Daily Bonus Odebrany!",
            description=f"Dostałeś dzisiaj: **{reward} pkt**",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed_success)

    @app_commands.command(name="ranking", description="Top 10 graczy")
    async def ranking(self, interaction: discord.Interaction):
        sorted_users = sorted(self.bot.user_data.items(), key=lambda x: x[1]['points'], reverse=True)[:10]
        desc = ""
        for i, (uid, data) in enumerate(sorted_users, 1):
            desc += f"**{i}.** <@{uid}> — `{data['points']:.1f} pkt`\n"
        embed = discord.Embed(title="🏆 Ranking", description=desc, color=0xe67e22)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Event(bot))
    
