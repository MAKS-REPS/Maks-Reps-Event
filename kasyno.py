import discord
from discord.ext import commands
from discord import app_commands, ui
import random
import asyncio
from datetime import datetime

# --- LOGIKA KART ---
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
    while wartosc > 21 and asy > 0:
        wartosc -= 10
        asy -= 1
    return wartosc

def wez_talie():
    kolory = ['P', 'K', 'T', 'R'] 
    figury = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    talia = [f"{f}{k}" for f in figury for k in kolory]
    random.shuffle(talia)
    return talia

def formatuj_karty(reka):
    return " ".join([f"[{karta}]" for karta in reka])

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
        wartosc_gracza = oblicz_reke(self.reka_gracza)
        karty_gracza = formatuj_karty(self.reka_gracza)
        if not koniec:
            karty_krupiera = f"[{self.reka_krupiera[0]}] [??]"
            tytul, kolor = "Blackjack | Twoja tura", 0xffffff
            opis = f"**Stawka:** {self.amount} pkt\n\n**Krupier:** {karty_krupiera}\n**Twoje karty:** {karty_gracza} = {wartosc_gracza}"
        else:
            return karty_gracza, wartosc_gracza, formatuj_karty(self.reka_krupiera), oblicz_reke(self.reka_krupiera)
        embed = discord.Embed(title=tytul, description=opis, color=kolor)
        return embed, wartosc_gracza

    async def sprawdz_wynik(self, interaction, wg, wk):
        d = self.bot.get_user(self.user_id)
        karty_gracza, _, karty_krupiera, _ = self.stworz_embed(koniec=True)
        if wg > 21: tytul, kolor, wynik_txt = "Blackjack | Przegrana", 0xff0000, f"-{self.amount} pkt"
        elif wk > 21 or wg > wk: 
            d["points"] += (self.amount * 2)
            tytul, kolor, wynik_txt = "Blackjack | Wygrana", 0x00ff00, f"+{self.amount} pkt"
        elif wg < wk: tytul, kolor, wynik_txt = "Blackjack | Przegrana", 0xff0000, f"-{self.amount} pkt"
        else: 
            d["points"] += self.amount
            tytul, kolor, wynik_txt = "Blackjack | Remis", 0xffff00, "0 pkt (Zwrot)"
        self.bot.save_data()
        emb = discord.Embed(title=tytul, description=f"**Twoje:** {karty_gracza} ({wg})\n**Krupier:** {karty_krupiera} ({wk})\n\n**Wynik:** {wynik_txt}", color=kolor)
        for child in self.children: child.disabled = True
        await interaction.edit_original_response(embed=emb, view=self)

    @ui.button(label="Dobierz", style=discord.ButtonStyle.primary)
    async def hit(self, interaction: discord.Interaction, button: ui.Button):
        self.reka_gracza.append(self.talia.pop())
        if oblicz_reke(self.reka_gracza) >= 21: await self.stand(interaction, button)
        else: await interaction.response.edit_message(embed=self.stworz_embed()[0], view=self)

    @ui.button(label="Stoj", style=discord.ButtonStyle.secondary)
    async def stand(self, interaction: discord.Interaction, button: ui.Button):
        wg, wk = oblicz_reke(self.reka_gracza), oblicz_reke(self.reka_krupiera)
        while wk < 17 and wg <= 21:
            self.reka_krupiera.append(self.talia.pop())
            wk = oblicz_reke(self.reka_krupiera)
        if not interaction.response.is_done(): await interaction.response.defer()
        await self.sprawdz_wynik(interaction, wg, wk)

class CasinoMenu(ui.View):
    def __init__(self, bot, user_id, amount):
        super().__init__(timeout=60)
        self.bot, self.user_id, self.amount = bot, user_id, amount

    @ui.button(label="Blackjack", style=discord.ButtonStyle.primary)
    async def btn_bj(self, interaction: discord.Interaction, button: ui.Button):
        d = self.bot.get_user(self.user_id)
        d["points"] -= self.amount
        self.bot.save_data()
        view = BlackjackGame(self.bot, self.user_id, self.amount)
        embed, wg = view.stworz_embed()
        await interaction.response.edit_message(embed=embed, view=view)
        if wg == 21: await view.stand(interaction, button)

    @ui.button(label="Ruletka", style=discord.ButtonStyle.danger)
    async def btn_roulette(self, interaction: discord.Interaction, button: ui.Button):
        d = self.bot.get_user(self.user_id)
        d["points"] -= self.amount
        await interaction.response.edit_message(content="🎰 **Losowanie...**", embed=None, view=None)
        await asyncio.sleep(1.5)
        if random.random() > 0.52:
            d["points"] += (self.amount * 2)
            emb = discord.Embed(title="Ruletka | Wygrana", description=f"✨ +{self.amount} pkt", color=0x00ff00)
        else:
            emb = discord.Embed(title="Ruletka | Przegrana", description=f"💀 -{self.amount} pkt", color=0xff0000)
        self.bot.save_data()
        await interaction.edit_original_response(content=None, embed=emb)

class Kasyno(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="hazard", description="Graj o punkty!") # ZMIENIONO NA HAZARD
    async def hazard(self, interaction: discord.Interaction, stawka: int):
        d = self.bot.get_user(interaction.user.id)
        if d["points"] < stawka: return await interaction.response.send_message("Brak punktów!", ephemeral=True)
        embed = discord.Embed(title="Kasyno", description=f"Stawka: **{stawka} pkt**\nWybierz grę:", color=0xffffff)
        await interaction.response.send_message(embed=embed, view=CasinoMenu(self.bot, interaction.user.id, stawka))

async def setup(bot): await bot.add_cog(Kasyno(bot))
