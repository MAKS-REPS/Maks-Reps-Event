import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="daj", description="Dodaj punkty")
    @app_commands.checks.has_permissions(administrator=True)
    async def daj(self, interaction: discord.Interaction, user: discord.Member, pkt: float):
        d = self.bot.get_user(user.id)
        d["points"] += pkt
        self.bot.save_data()
        await interaction.response.send_message(f"✅ Dodano **{pkt} pkt** dla {user.mention}", ephemeral=True)

    @app_commands.command(name="odbierz_punkty", description="Zabierz punkty")
    @app_commands.checks.has_permissions(administrator=True)
    async def odbierz_punkty(self, interaction: discord.Interaction, user: discord.Member, pkt: float):
        d = self.bot.get_user(user.id)
        d["points"] = max(0, d["points"] - pkt)
        self.bot.save_data()
        await interaction.response.send_message(f"✅ Zabrano **{pkt} pkt** od {user.mention}", ephemeral=True)

    @app_commands.command(name="happyhour", description="Mnożnik punktów")
    @app_commands.checks.has_permissions(administrator=True)
    async def hh(self, interaction: discord.Interaction, mnoznik: int, minuty: int):
        self.bot.point_multiplier = mnoznik
        await interaction.response.send_message(f"⚡ HAPPY HOUR x{mnoznik} przez {minuty} min!")
        await asyncio.sleep(minuty * 60)
        self.bot.point_multiplier = 1
        await interaction.channel.send("⏳ Happy Hour zakończony.")

async def setup(bot):
    await bot.add_cog(Admin(bot))
