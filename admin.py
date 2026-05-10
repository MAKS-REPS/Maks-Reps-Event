import discord
from discord.ext import commands
from discord import app_commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="admin_daj_punkty")
    @app_commands.checks.has_permissions(administrator=True)
    async def add(self, interaction, member: discord.Member, ilosc: float):
        d = self.bot.get_user(member.id)
        d["points"] += ilosc
        self.bot.save_data()
        await interaction.response.send_message(f"✅ Dodano **{ilosc} pkt** dla {member.mention}")

    @app_commands.command(name="admin_usun_punkty")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove(self, interaction, member: discord.Member, ilosc: float):
        d = self.bot.get_user(member.id)
        d["points"] -= ilosc
        self.bot.save_data()
        await interaction.response.send_message(f"❌ Odjęto **{ilosc} pkt** od {member.mention}")

async def setup(bot):
    await bot.add_cog(Admin(bot))
