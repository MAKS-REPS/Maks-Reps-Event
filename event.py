import discord
from discord.ext import commands
from discord import app_commands, ui
import math
import asyncio

TICKET_CATEGORY_ID = 1486842150661656767
NAZWA_EVENTU = "Maks Reps Event"

class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not self.bot.event_active: return
        uid = str(message.author.id)
        now = asyncio.get_event_loop().time()
        if now - self.cooldowns.get(uid, 0) > 5:
            d = self.bot.get_user(message.author.id)
            d["points"] += 2
            self.cooldowns[uid] = now
            self.bot.save_data()

    @app_commands.command(name="level", description="Profil gracza")
    async def level(self, interaction: discord.Interaction):
        d = self.bot.get_user(interaction.user.id)
        lvl = min(math.floor(d["points"] / 100) + 1, 50)
        embed = discord.Embed(title=f"Profil: {interaction.user.name}", color=0xf1c40f)
        embed.add_field(name="Level", value=str(lvl), inline=True)
        embed.add_field(name="Punkty", value=f"{d['points']:.1f}", inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="zadania", description="Lista dostępnych zadań")
    async def zadania(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📋 Lista Zadań - Maks Reps", color=0x3498db)
        embed.add_field(name="📦 Zamówienie paki", value="Nagroda: **100 pkt**", inline=False)
        embed.add_field(name="📱 TikTok Follow", value="Nagroda: **30 pkt**", inline=False)
        embed.add_field(name="👥 Zaproszenia (2 os.)", value="Nagroda: **50 pkt**", inline=False)
        embed.set_footer(text="Użyj /odbierz, aby wysłać dowód.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ranking", description="Top 10 graczy")
    async def ranking(self, interaction: discord.Interaction):
        sorted_users = sorted(self.bot.user_data.items(), key=lambda x: x[1]['points'], reverse=True)[:10]
        desc = ""
        for i, (uid, data) in enumerate(sorted_users, 1):
            desc += f"**{i}.** <@{uid}> — `{data['points']:.1f} pkt`\n"
        embed = discord.Embed(title="🏆 Ranking", description=desc, color=0xe67e22)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="odbierz", description="Otwórz ticket")
    async def odbierz(self, interaction: discord.Interaction):
        view = ui.View()
        select = ui.Select(placeholder="Wybierz zadanie...")
        select.add_option(label="Zamówienie paki", value="Paka")
        select.add_option(label="TikTok Follow", value="TikTok")
        
        async def callback(inter):
            cat = inter.guild.get_channel(TICKET_CATEGORY_ID)
            ch = await inter.guild.create_text_channel(f"ticket-{inter.user.name}", category=cat)
            await ch.send(f"{inter.user.mention} Prześlij tutaj dowód wykonania zadania.")
            await inter.response.send_message(f"Otwarto: {ch.mention}", ephemeral=True)
            
        select.callback = callback
        view.add_item(select)
        await interaction.response.send_message("Wybierz zadanie:", view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Event(bot))
