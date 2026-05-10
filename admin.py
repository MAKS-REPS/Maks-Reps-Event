import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="daj_punkty", description="Dodaj punkty użytkownikowi")
    @app_commands.checks.has_permissions(administrator=True)
    async def daj_punkty(self, interaction: discord.Interaction, uzytkownik: discord.Member, ilosc: float):
        d = self.bot.get_user(uzytkownik.id)
        d["points"] += ilosc
        self.bot.save_data()
        
        emb = discord.Embed(description=f"✅ Dodano **{ilosc} pkt** dla {uzytkownik.mention}", color=0x00FF00)
        await interaction.response.send_message(embed=emb)

    @app_commands.command(name="zabierz_punkty", description="Zabierz punkty użytkownikowi")
    @app_commands.checks.has_permissions(administrator=True)
    async def zabierz_punkty(self, interaction: discord.Interaction, uzytkownik: discord.Member, ilosc: float):
        d = self.bot.get_user(uzytkownik.id)
        d["points"] = max(0, d["points"] - ilosc)
        self.bot.save_data()
        
        emb = discord.Embed(description=f"✅ Zabrano **{ilosc} pkt** od {uzytkownik.mention}", color=0xFF0000)
        await interaction.response.send_message(embed=emb)

    @app_commands.command(name="happyhour", description="Mnożnik punktów")
    @app_commands.checks.has_permissions(administrator=True)
    async def happyhour(self, interaction: discord.Interaction, mnoznik: int, minuty: int):
        self.bot.point_multiplier = mnoznik
        await interaction.response.send_message(f"⚡ Happy Hour x{mnoznik} aktywny przez {minuty} min!")
        await asyncio.sleep(minuty * 60)
        self.bot.point_multiplier = 1
        await interaction.channel.send("⏳ Happy Hour zakończony.")

async def setup(bot):
    await bot.add_cog(Admin(bot))
