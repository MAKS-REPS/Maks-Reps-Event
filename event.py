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
            d = self.bot.get_user(uid)
            d["points"] += 2
            self.cooldowns[uid] = now
            self.bot.save_data()

    @app_commands.command(name="level", description="Pokazuje twój profil")
    async def level(self, interaction: discord.Interaction):
        d = self.bot.get_user(interaction.user.id)
        pts = d["points"]
        lvl = min(math.floor(pts / 100) + 1, 50)
        progress = int(pts % 100)
        
        embed = discord.Embed(title=f"Profil: {interaction.user.display_name}", color=0x2b2d31)
        embed.set_author(name=NAZWA_EVENTU)
        embed.add_field(name="✨ Poziom", value=f"**{lvl}**", inline=True)
        embed.add_field(name="💰 Punkty", value=f"**{pts:.1f}**", inline=True)
        
        # Pasek postępu (zdjęcie 3)
        bar = "🟩" * (progress // 10) + "⬛" * (10 - (progress // 10))
        embed.add_field(name=f"Postęp do Levelu {lvl+1}", value=f"{bar} **{progress}%**", inline=False)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ranking", description="Top 10 osób w evencie")
    async def ranking(self, interaction: discord.Interaction):
        # Sortowanie (zdjęcie 4)
        sorted_users = sorted(self.bot.user_data.items(), key=lambda x: x[1]['points'], reverse=True)[:10]
        
        embed = discord.Embed(title=f"🏆 Ranking - {NAZWA_EVENTU}", color=discord.Color.gold())
        description = ""
        for i, (uid, data) in enumerate(sorted_users, 1):
            user = self.bot.get_user(int(uid))
            name = f"<@{uid}>"
            description += f"**{i}.** {name} — `{data['points']:.1f} pkt` (Lvl {min(math.floor(data['points']/100)+1, 50)})\n"
        
        embed.description = description if description else "Brak danych."
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="odbierz", description="Odbierz punkty za zadanie")
    async def odbierz(self, interaction: discord.Interaction):
        view = ui.View()
        select = ui.Select(placeholder="Wybierz zadanie do weryfikacji...")
        select.add_option(label="Zamówienie paki z linku", emoji="📦", value="Paka")
        select.add_option(label="Obserwacja na TikToku", emoji="📱", value="TikTok")
        
        async def callback(inter):
            cat = inter.guild.get_channel(TICKET_CATEGORY_ID)
            ch = await inter.guild.create_text_channel(f"ticket-{inter.user.name}", category=cat)
            embed = discord.Embed(title="Weryfikacja", description=f"Zadanie: **{select.values[0]}**", color=0x2ecc71)
            await ch.send(content=f"{inter.user.mention} | Administracja", embed=embed)
            await inter.response.send_message(f"Otwarto ticket: {ch.mention}", ephemeral=True)

        select.callback = callback
        view.add_item(select)
        await interaction.response.send_message("Wybierz opcję:", view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Event(bot))
