import discord
from discord.ext import commands
from discord import app_commands, ui
import random
import asyncio

class RuletkaGame(ui.View):
    def __init__(self, bot, user_id, amount):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.amount = amount

    async def start_animation(self, interaction, bet_type):
        # Stary interfejs animacji (kwadraciki)
        frames = [
            "🟥 ⬛ 🟥 ⬛ 🟥",
            "⬛ 🟥 ⬛ 🟥 ⬛",
            "🟥 ⬛ 🟩 ⬛ 🟥",
            "⬛ 🟥 ⬛ 🟥 ⬛"
        ]
        
        for frame in frames:
            await interaction.edit_original_response(content=f"🎰 Losowanie: \n{frame}", view=None)
            await asyncio.sleep(0.5)

        # Losowanie 50/50 dla kolorów
        rand = random.randint(1, 100)
        if rand == 1: # Bardzo rzadki zielony (1%)
            result_color = "zielony"
            result_num = 0
        else:
            result_color = random.choice(["czerwony", "czarny"])
            result_num = random.randint(1, 36)

        win = False
        if bet_type == result_color:
            win = True
        elif bet_type == "parzyste" and result_num != 0 and result_num % 2 == 0:
            win = True
        elif bet_type == "nieparzyste" and result_num != 0 and result_num % 2 != 0:
            win = True

        d = self.bot.get_user(self.user_id)
        if win:
            d["points"] += self.amount
            msg = f"✅ Wypadło: **{result_color.upper()}** ({result_num}). Wygrałeś **{self.amount * 2} pkt**!"
        else:
            d["points"] -= self.amount
            msg = f"❌ Wypadło: **{result_color.upper()}** ({result_num}). Przegrałeś **{self.amount} pkt**."
        
        self.bot.save_data()
        await interaction.edit_original_response(content=msg)

    @ui.button(label="Czerwone", style=discord.ButtonStyle.danger)
    async def red(self, interaction, btn):
        await interaction.response.defer()
        await self.start_animation(interaction, "czerwony")

    @ui.button(label="Czarne", style=discord.ButtonStyle.secondary)
    async def black(self, interaction, btn):
        await interaction.response.defer()
        await self.start_animation(interaction, "czarny")

    @ui.button(label="Parzyste", style=discord.ButtonStyle.primary)
    async def even(self, interaction, btn):
        await interaction.response.defer()
        await self.start_animation(interaction, "parzyste")

    @ui.button(label="Nieparzyste", style=discord.ButtonStyle.primary)
    async def odd(self, interaction, btn):
        await interaction.response.defer()
        await self.start_animation(interaction, "nieparzyste")

class Kasyno(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kasyno", description="Zagraj w ruletkę")
    async def kasyno(self, interaction: discord.Interaction, stawka: float):
        d = self.bot.get_user(interaction.user.id)
        if d["points"] < stawka:
            return await interaction.response.send_message("Brak punktów!", ephemeral=True)
        
        embed = discord.Embed(title="🎰 Ruletka", description=f"Stawka: **{stawka}**", color=0x2b2d31)
        await interaction.response.send_message(embed=embed, view=RuletkaGame(self.bot, interaction.user.id, stawka), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Kasyno(bot))
