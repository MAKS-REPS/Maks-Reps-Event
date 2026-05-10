import discord
from discord.ext import commands
from discord import app_commands, ui
import random

class Kasyno(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kasyno", description="Graj o punkty (stawka 2 pkt)")
    async def kasyno(self, interaction):
        d = self.bot.get_user(interaction.user.id)
        if d["points"] < 2:
            return await interaction.response.send_message("Brak punktów!", ephemeral=True)

        view = ui.View()
        btn_bj = ui.Button(label="Blackjack", style=discord.ButtonStyle.primary)
        btn_rl = ui.Button(label="Ruletka", style=discord.ButtonStyle.danger)

        async def bj_callback(inter):
            res = random.choice([True, False])
            u = self.bot.get_user(inter.user.id)
            if res:
                u["points"] += 2
                await inter.response.send_message("Wygrałeś w Blackjacka! +2 pkt")
            else:
                u["points"] -= 2
                await inter.response.send_message("Przegrałeś w Blackjacka! -2 pkt")
            self.bot.save_data()

        btn_bj.callback = bj_callback
        view.add_item(btn_bj)
        view.add_item(btn_rl)
        await interaction.response.send_message("W co grasz?", view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Kasyno(bot))
