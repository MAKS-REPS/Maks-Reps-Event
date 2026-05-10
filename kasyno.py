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
        if figura in ['J', 'Q', 'K']: wartosc += 10
        elif figura == 'A': asy += 1; wartosc += 11
        else: wartosc += int(figura)
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

class BlackjackGame(ui.View):
    def __init__(self, bot, user_id, amount):
        super().__init__(timeout=60)
        self.bot, self.user_id, self.amount = bot, user_id, amount
        self.talia = wez_talie()
        self.reka_gracza = [self.talia.pop(), self.talia.pop()]
        self.reka_krupiera = [self.talia.pop(), self.talia.pop()]

    def stworz_embed(self, koniec=False):
        wg = oblicz_reke(self.reka_gracza)
        karty_g = " ".join([f"[{k}]" for k in self.reka_gracza])
        
        if not koniec:
            embed = discord.Embed(title="Blackjack | Twoja tura", color=0x36393f)
            embed.description = (
                f"**Stawka:** {self.amount} pkt\n\n"
                f"**Krupier:** [{self.reka_krupiera[0]}] [??]\n"
                f"**Twoje karty:** {karty_g} = {wg}\n\n"
                f"Dobierz karte lub zostaw.\n"
                f"**Cel:** Miej wiecej niz krupier, ale nie przekrocz 21"
            )
        else:
            return karty_g, wg, " ".join([f"[{k}]" for k in self.reka_krupiera]), oblicz_reke(self.reka_krupiera)
        
        embed.set_footer(text=f"Maks Reps Event | Dziś o {datetime.now().strftime('%H:%M')}")
        return embed, wg

    @ui.button(label="Dobierz", style=discord.ButtonStyle.primary)
    async def hit(self, interaction: discord.Interaction, button: ui.Button):
        self.reka_gracza.append(self.talia.pop())
        if oblicz_reke(self.reka_gracza) >= 21: await self.stand(interaction, button)
        else: await interaction.response.edit_message(embed=self.stworz_embed()[0], view=self)

    @ui.button(label="Stoj", style=discord.ButtonStyle.secondary)
    async def stand(self, interaction: discord.Interaction, button: ui.Button):
        wg = oblicz_reke(self.reka_gracza)
        wk = oblicz_reke(self.reka_krupiera)
        while wk < 17 and wg <= 21:
            self.reka_krupiera.append(self.talia.pop())
            wk = oblicz_reke(self.reka_krupiera)
        
        d = self.bot.get_user(self.user_id)
        kg, wg, kk, wk = self.stworz_embed(koniec=True)
        
        if wg > 21: win, txt, color = False, "Przegrana", 0xff0000
        elif wk > 21 or wg > wk: 
            d["points"] += (self.amount * 2)
            win, txt, color = True, "Wygrana", 0x00ff00
        elif wg < wk: win, txt, color = False, "Przegrana", 0xff0000
        else:
            d["points"] += self.amount
            win, txt, color = None, "Remis", 0xffff00

        self.bot.save_data()
        emb = discord.Embed(title=f"Blackjack | {txt}", color=color)
        emb.description = (
            f"**Twoje karty:** {kg} = {wg}\n"
            f"**Krupier:** {kk} = {wk}\n\n"
            f"**Stawka:** {self.amount} pkt\n"
            f"**Wynik:** {'+' if win else '-' if win==False else ''}{self.amount if win is not None else 0} pkt\n\n"
            f"Uzyj /hazard aby zagrac ponownie"
        )
        emb.set_footer(text=f"Maks Reps Event | Dziś o {datetime.now().strftime('%H:%M')}")
        for c in self.children: c.disabled = True
        
        if not interaction.response.is_done():
            await interaction.response.edit_message(embed=emb, view=self)
        else:
            await interaction.edit_original_response(embed=emb, view=self)

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
        await interaction.response.edit_message(content="🎰 Losowanie...", embed=None, view=None)
        await asyncio.sleep(2)
        
        win = random.random() > 0.55 # Szansa na wygraną
        if win:
            d["points"] += (self.amount * 2)
            res, color, p_txt = "Wygrana", 0x00ff00, f"+{self.amount}"
        else:
            res, color, p_txt = "Przegrana", 0xff0000, f"-{self.amount}"
        
        self.bot.save_data()
        emb = discord.Embed(title=f"Ruletka | {res}", color=color)
        emb.description = f"**Wynik:** {p_txt} pkt\n\nUzyj /hazard aby zagrac ponownie"
        emb.set_footer(text=f"Maks Reps Event | Dziś o {datetime.now().strftime('%H:%M')}")
        await interaction.edit_original_response(content=None, embed=emb)

class Kasyno(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="hazard", description="Graj o punkty!")
    async def hazard(self, interaction: discord.Interaction, stawka: int):
        d = self.bot.get_user(interaction.user.id)
        if d["points"] < stawka:
            return await interaction.response.send_message(f"❌ Nie masz wystarczająco punktów! (Saldo: {d['points']:.1f})", ephemeral=True)
        
        embed = discord.Embed(title="Kasyno Maks Reps Event", color=0x36393f)
        embed.description = (
            f"Wybierz gre i sprobuj podwoic swoje punkty!\n\n"
            f"**Twoja stawka:** {stawka} pkt\n"
            f"**Twoje saldo:** {d['points']:.1f} pkt\n\n"
            f"**Dostepne gry:**\n"
            f"**1.** Blackjack | Dobieraj karty, nie przekrocz 21.\nWygrana: x2\n"
            f"**2.** Ruletka | Postaw na kolor i wygraj. Czerwone/Czarne: x2, Zielone: x14\n\n"
            f"Wygrane i przegrane sa natychmiast rozliczane"
        )
        embed.set_footer(text=f"Maks Reps Event | Dziś o {datetime.now().strftime('%H:%M')}")
        await interaction.response.send_message(embed=embed, view=CasinoMenu(self.bot, interaction.user.id, stawka))

async def setup(bot): await bot.add_cog(Kasyno(bot))
