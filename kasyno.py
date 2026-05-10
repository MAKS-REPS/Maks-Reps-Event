import discord
from discord.ext import commands
from discord import app_commands, ui
import random
import asyncio

def oblicz_reke(reka):
    wartosc = 0
    asy = 0
    for karta in reka:
        figura = karta[:-1]
        if figura in ['J', 'Q', 'K']:
            wartosc += 10
        elif figura == 'A':
            asy += 1
            wartosc += 11
        else:
            wartosc += int(figura)
    while wartosc > 21 and asy:
        wartosc -= 10
        asy -= 1
    return wartosc

def wez_talie():
    kolory = ['♠️', '♥️', '♦️', '♣️']
    figury = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    talia = [f"{f}{k}" for f in figury for k in kolory]
    random.shuffle(talia)
    return talia

class BlackjackGame(ui.View):
    def __init__(self, bot, user_id, amount):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.amount = amount
        self.talia = wez_talie()
        self.reka_gracza = [self.talia.pop(), self.talia.pop()]
        self.reka_krupiera = [self.talia.pop(), self.talia.pop()]

    def stworz_embed(self, koniec=False):
        embed = discord.Embed(title="Blackjack ♠️", color=0x2b2d31)
        
        # Ręka krupiera
        if koniec:
            wartosc_krupiera = oblicz_reke(self.reka_krupiera)
            karty_krupiera = ", ".join(self.reka_krupiera)
            embed.add_field(name="Ręka krupiera:", value=f"{karty_krupiera}\n[{wartosc_krupiera}]", inline=False)
        else:
            karty_krupiera = f"?, {self.reka_krupiera[1]}"
            embed.add_field(name="Ręka krupiera:", value=f"{karty_krupiera}\n[?]", inline=False)

        # Ręka gracza
        wartosc_gracza = oblicz_reke(self.reka_gracza)
        karty_gracza = ", ".join(self.reka_gracza)
        embed.add_field(name="Twoja ręka:", value=f"{karty_gracza}\n[{wartosc_gracza}]", inline=False)
        return embed, wartosc_gracza

    async def sprawdz_wynik(self, interaction, wartosc_gracza, wartosc_krupiera):
        d = self.bot.get_user(self.user_id)
        if wartosc_gracza > 21:
            d["points"] -= self.amount
            wynik = f"Przekroczyłeś 21! Przegrywasz **{self.amount} pkt**."
            kolor = 0xe74c3c
        elif wartosc_krupiera > 21 or wartosc_gracza > wartosc_krupiera:
            d["points"] += self.amount
            wynik = f"Wygrywasz! Zyskujesz **{self.amount} pkt**."
            kolor = 0x2ecc71
        elif wartosc_gracza < wartosc_krupiera:
            d["points"] -= self.amount
            wynik = f"Krupier wygrywa. Tracisz **{self.amount} pkt**."
            kolor = 0xe74c3c
        else:
            wynik = "Remis! Odzyskujesz stawkę."
            kolor = 0xf1c40f
            
        self.bot.save_data()
        embed, _ = self.stworz_embed(koniec=True)
        embed.color = kolor
        embed.description = wynik
        await interaction.edit_original_response(embed=embed, view=None)

    @ui.button(label="Dobierz (Hit)", style=discord.ButtonStyle.primary)
    async def hit(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id: return
        self.reka_gracza.append(self.talia.pop())
        embed, wartosc_gracza = self.stworz_embed()
        
        if wartosc_gracza > 21:
            await self.sprawdz_wynik(interaction, wartosc_gracza, oblicz_reke(self.reka_krupiera))
        else:
            await interaction.response.edit_message(embed=embed, view=self)

    @ui.button(label="Czekaj (Stand)", style=discord.ButtonStyle.danger)
    async def stand(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id: return
        wartosc_gracza = oblicz_reke(self.reka_gracza)
        wartosc_krupiera = oblicz_reke(self.reka_krupiera)
        
        while wartosc_krupiera < 17:
            self.reka_krupiera.append(self.talia.pop())
            wartosc_krupiera = oblicz_reke(self.reka_krupiera)
            
        await self.sprawdz_wynik(interaction, wartosc_gracza, wartosc_krupiera)


class RuletkaGame(ui.View):
    def __init__(self, bot, user_id, amount):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.amount = amount

    async def start_animation(self, interaction, bet_type):
        frames = ["🟥 ⬛ 🟥 ⬛ 🟥", "⬛ 🟥 ⬛ 🟥 ⬛", "🟥 ⬛ 🟩 ⬛ 🟥", "⬛ 🟥 ⬛ 🟥 ⬛"]
        for frame in frames:
            await interaction.edit_original_response(content=f"🎰 Losowanie: \n{frame}", view=None)
            await asyncio.sleep(0.5)

        rand = random.randint(1, 100)
        if rand == 1:
            result_color, result_num = "zielony", 0
        else:
            result_color = random.choice(["czerwony", "czarny"])
            result_num = random.randint(1, 36)

        win = (bet_type == result_color) or \
              (bet_type == "parzyste" and result_num != 0 and result_num % 2 == 0) or \
              (bet_type == "nieparzyste" and result_num != 0 and result_num % 2 != 0)

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

    @app_commands.command(name="kasyno", description="Zagraj w kasynie")
    @app_commands.choices(gra=[
        app_commands.Choice(name="Blackjack", value="blackjack"),
        app_commands.Choice(name="Ruletka", value="ruletka")
    ])
    async def kasyno(self, interaction: discord.Interaction, gra: app_commands.Choice[str], stawka: float):
        if stawka <= 0: return await interaction.response.send_message("Stawka musi być większa niż 0!", ephemeral=True)
        d = self.bot.get_user(interaction.user.id)
        if d["points"] < stawka: return await interaction.response.send_message("Brak punktów!", ephemeral=True)

        if gra.value == "blackjack":
            view = BlackjackGame(self.bot, interaction.user.id, stawka)
            embed, wartosc_gracza = view.stworz_embed()
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            if wartosc_gracza == 21:
                await view.sprawdz_wynik(interaction, wartosc_gracza, oblicz_reke(view.reka_krupiera))
        else:
            embed = discord.Embed(title="🎰 Ruletka", description=f"Stawka: **{stawka}**", color=0x2b2d31)
            await interaction.response.send_message(embed=embed, view=RuletkaGame(self.bot, interaction.user.id, stawka), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Kasyno(bot))
    
