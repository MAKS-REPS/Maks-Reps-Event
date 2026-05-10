import discord
from discord.ext import commands
from discord import app_commands, ui
import random

class KasynoView(ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id

    @ui.button(label="🎰 Ruletka", style=discord.ButtonStyle.danger)
    async def ruletka(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id: return
        view = RuletkaGame(self.bot, self.user_id)
        await interaction.response.edit_message(content="Wybierz kolor w Ruletce (Stawka: 2 pkt):", view=view)

    @ui.button(label="🃏 Blackjack", style=discord.ButtonStyle.primary)
    async def blackjack(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id: return
        # Logika BJ (uproszczona)
        d = self.bot.get_user(self.user_id)
        if d["points"] < 2: return await interaction.response.send_message("Brak punktów!", ephemeral=True)
        
        res = random.choice(["win", "lose"])
        if res == "win":
            d["points"] += 2
            msg = "🃏 **Blackjack!** Wygrałeś 2 pkt."
        else:
            d["points"] -= 2
            msg = "🃏 **Przegrałeś!** Straciłeś 2 pkt."
        self.bot.save_data()
        await interaction.response.edit_message(content=msg, view=None)

class RuletkaGame(ui.View):
    def __init__(self, bot, user_id):
        super().__init__()
        self.bot = bot
        self.user_id = user_id

    async def play(self, interaction, color_choice):
        d = self.bot.get_user(self.user_id)
        if d["points"] < 2: return
        
        result = random.choices(["red", "black", "green"], weights=[47, 47, 6])[0]
        if color_choice == result:
            prize = 28 if result == "green" else 4
            d["points"] += prize
            msg = f"🟢 Wypadło **{result}**! Wygrałeś!"
        else:
            d["points"] -= 2
            msg = f"🔴 Wypadło **{result}**. Przegrałeś."
        self.bot.save_data()
        await interaction.response.edit_message(content=msg, view=None)

    @ui.button(label="Czerwone", style=discord.ButtonStyle.danger)
    async def red(self, interaction, btn): await self.play(interaction, "red")
    @ui.button(label="Czarne", style=discord.ButtonStyle.secondary)
    async def black(self, interaction, btn): await self.play(interaction, "black")

class Kasyno(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kasyno", description="Wybierz grę w kasynie")
    async def kasyno(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Maks Reps Kasyno", description="Wybierz grę, w którą chcesz zagrać za 2 pkt.")
        await interaction.response.send_message(embed=embed, view=KasynoView(self.bot, interaction.user.id), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Kasyno(bot))
