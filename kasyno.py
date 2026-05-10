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
        frames = [
            "**> 🟥 <** ⬛ 🟥 ⬛ 🟥",
            "🟥 **> ⬛ <** 🟥 ⬛ 🟥",
            "🟥 ⬛ **> 🟥 <** ⬛ 🟥",
            "🟥 ⬛ 🟥 **> ⬛ <** 🟥",
            "🟥 ⬛ 🟥 ⬛ **> 🟥 <**",
            "**> ⬛ <** 🟥 ⬛ 🟥 ⬛",
            "⬛ **> 🟩 <** ⬛ 🟥 ⬛"
        ]
        
        for frame in frames:
            await interaction.edit_original_response(
                content=f"🎰 **TRWA LOSOWANIE...**\n\n{frame}\n\n*Powodzenia!*", 
                view=None
            )
            await asyncio.sleep(0.4)

        rand = random.randint(1, 1000)
        
        if rand <= 5: # 0.5% szansy
            result_color = "zielony"
            result_emoji = "🟩"
            result_num = 0
        elif rand <= 503:
            result_color = "czerwony"
            result_emoji = "🟥"
            result_num = random.choice([1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36])
        else:
            result_color = "czarny"
            result_emoji = "⬛"
            result_num = random.choice([2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35])

        win = False
        multiplier = 0

        if bet_type == result_color:
            win = True
            multiplier = 10 if result_color == "zielony" else 2
        elif bet_type == "parzyste" and result_num != 0 and result_num % 2 == 0:
            win = True
            multiplier = 2
        elif bet_type == "nieparzyste" and result_num != 0 and result_num % 2 != 0:
            win = True
            multiplier = 2

        d = self.bot.get_user(self.user_id)
        if win:
            prize = self.amount * (multiplier - 1)
            d["points"] += prize
            status = "WYGRANA! 🎉"
            color_embed = 0x2ecc71
        else:
            d["points"] -= self.amount
            status = "PRZEGRANA"
            color_embed = 0xe74c3c
        
        self.bot.save_data()

        embed = discord.Embed(title=f"🎰 Wynik: {status}", color=color_embed)
        embed.description = f"Wypadło: {result_emoji} **{result_color.upper()}** ({result_num})"
        
        if win:
            embed.add_field(name="Nagroda", value=f"+{self.amount * multiplier:.1f} pkt")
        else:
            embed.add_field(name="Strata", value=f"-{self.amount:.1f} pkt")
        
        embed.set_footer(text=f"Twoje saldo: {d['points']:.1f} pkt")
        await interaction.edit_original_response(content=None, embed=embed)

    @ui.button(label="Czerwone (x2)", style=discord.ButtonStyle.danger)
    async def red(self, interaction: discord.Interaction, btn):
        await interaction.response.defer()
        await self.start_animation(interaction, "czerwony")

    @ui.button(label="Czarne (x2)", style=discord.ButtonStyle.secondary)
    async def black(self, interaction: discord.Interaction, btn):
        await interaction.response.defer()
        await self.start_animation(interaction, "czarny")

    @ui.button(label="Zielone (x10)", style=discord.ButtonStyle.success)
    async def green(self, interaction: discord.Interaction, btn):
        await interaction.response.defer()
        await self.start_animation(interaction, "zielony")

    @ui.button(label="Parzyste", style=discord.ButtonStyle.primary)
    async def even(self, interaction: discord.Interaction, btn):
        await interaction.response.defer()
        await self.start_animation(interaction, "parzyste")

    @ui.button(label="Nieparzyste", style=discord.ButtonStyle.primary)
    async def odd(self, interaction: discord.Interaction, btn):
        await interaction.response.defer()
        await self.start_animation(interaction, "nieparzyste")

class Kasyno(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kasyno", description="Zagraj w ruletkę o punkty")
    @app_commands.describe(stawka="Ile punktów chcesz postawić?")
    async def kasyno(self, interaction: discord.Interaction, stawka: float):
        if stawka <= 0:
            return await interaction.response.send_message("Stawka musi być większa niż 0!", ephemeral=True)
            
        d = self.bot.get_user(interaction.user.id)
        if d["points"] < stawka:
            return await interaction.response.send_message(f"Masz za mało punktów! (Posiadasz: {d['points']:.1f})", ephemeral=True)

        embed = discord.Embed(
            title="🎰 Maks Reps Ruletka",
            description=f"Obstawiasz: **{stawka} pkt**\nWybierz swój typ poniżej:",
            color=0x2b2d31
        )
        await interaction.response.send_message(embed=embed, view=RuletkaGame(self.bot, interaction.user.id, stawka), ephemeral=True)

# TO SĄ TE KLUCZOWE LINIE:
async def setup(bot):
    await bot.add_cog(Kasyno(bot))
