import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="happyhour", description="Uruchom mnożnik punktów na określony czas")
    @app_commands.checks.has_permissions(administrator=True)
    async def happyhour(self, interaction: discord.Interaction, mnoznik: int, minuty: int):
        self.bot.point_multiplier = mnoznik
        
        emb = discord.Embed(
            title="⚡ HAPPY HOUR!",
            description=f"Przez najbliższe **{minuty} minut** zdobywacie **x{mnoznik}** punktów za pisanie!",
            color=0xffffff
        )
        await interaction.response.send_message(embed=emb)
        
        await asyncio.sleep(minuty * 60)
        self.bot.point_multiplier = 1
        await interaction.channel.send("⏳ Happy Hour zakończony. Punkty wróciły do normy.")

async def setup(bot):
    await bot.add_cog(Admin(bot))
