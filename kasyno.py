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
        figura = karta[:-1] # Pobiera wszystko oprócz ostatniego znaku (koloru)
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
    # P = Pik, K = Kier, T = Trefl, R = Karo
    kolory = ['P', 'K', 'T', 'R'] 
    figury = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    talia = [f"{f}{k}" for f in figury for k in kolory]
    random.shuffle(talia)
    return talia

def formatuj_karty(reka):
    return " ".join([f"[{karta}]" for karta in reka])

# --- WIDOK BLACKJACKA ---
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
            tytul = "Blackjack | Twoja tura"
            kolor = 0x2b2d31
            opis = f"**Stawka:** {self.amount} pkt\n\n**Krupier:** {karty_krupiera}\n**Twoje karty:** {karty_gracza} = {wartosc_gracza}\n\nDobierz karte lub zostaw.\nCel: Miej wiecej niz krupier, ale nie przekrocz 21"
        else:
            wartosc_krupiera = oblicz_reke(self.reka_krupiera)
            karty_krupiera = formatuj_karty(self.reka_krupiera)
            # Wyniki i kolory są ustawiane w sprawdz_wynik()
            return karty_gracza, wartosc_gracza, karty_krupiera, wartosc_krupiera

        embed = discord.Embed(title=tytul, description=opis, color=kolor)
        embed.set_footer(text=f"Użyj /kasyno aby zagrać ponownie | Dziś o {datetime.now().strftime('%H:%M')}")
        return embed, wartosc_gracza

    async def sprawdz_wynik(self, interaction, wartosc_gracza, wartosc_krupiera):
        d = self.bot.get_user(self.user_id)
        karty_gracza, wg, karty_krupiera, wk = self.stworz_embed(koniec=True)
        
        if wg > 21:
            tytul = "Blackjack | Przegrana"
            wynik_txt = f"-{self.amount} pkt"
            kolor = 0xff0000
        elif wk > 21 or wg > wk:
            d["points"] += (self.amount * 2) # Zwraca stawkę i dodaje drugie tyle
            tytul = "Blackjack | Wygrana"
            wynik_txt = f"+{self.amount} pkt"
            kolor = 0x00ff00
        elif wg < wk:
            tytul = "Blackjack | Przegrana"
            wynik_txt = f"-{self.amount} pkt"
            kolor = 0xff0000
        else:
            d["points"] += self.amount # Zwraca stawkę (remis)
            tytul = "Blackjack | Remis"
            wynik_txt = "0 pkt (Zwrot stawki)"
            kolor = 0xffff00
            
        self.bot.save_data()
        
        opis = f"**Twoje karty:** {karty_gracza} = {wg}\n**Krupier:** {karty_krupiera} = {wk}\n\n**Stawka:** {self.amount} pkt\n**Wynik:** {wynik_txt}"
        embed = discord.Embed(title=tytul, description=opis, color=kolor)
        embed.set_footer(text=f"Użyj /kasyno aby zagrać ponownie | Dziś o {datetime.now().strftime('%H:%M')}")
        
        # Wyłączenie przycisków po grze
        for child in self.children:
            child.disabled = True
            
        await interaction.edit_original_response(embed=embed, view=self)

    @ui.button(label="Dobierz", style=discord.ButtonStyle.primary)
    async def hit(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id: return
        self.reka_gracza.append(self.talia.pop())
        embed, wartosc_gracza = self.stworz_embed()
        
        if wartosc_gracza >= 21: # Jeśli 21 lub więcej, koniec tury
            await self.stand(interaction, button)
        else:
            await interaction.response.edit_message(embed=embed, view=self)

    @ui.button(label="Stoj", style=discord.ButtonStyle.secondary)
    async def stand(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id: return
        wartosc_gracza = oblicz_reke(self.reka_gracza)
        wartosc_krupiera = oblicz_reke(self.reka_krupiera)
        
        # Krupier dobiera do 17
        while wartosc_krupiera < 17 and wartosc_gracza <= 21:
            self.reka_krupiera.append(self.talia.pop())
            wartosc_krupiera = oblicz_reke(self.reka_krupiera)
            
        await interaction.response.defer()
        await self.sprawdz_wynik(interaction, wartosc_gracza, wartosc_krupiera)


# --- MENU GŁÓWNE KASYNA ---
class CasinoMenu(ui.View):
    def __init__(self, bot, user_id, amount):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.amount = amount

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("To nie twój panel!", ephemeral=True)
            return False
        return True

    @ui.button(label="Blackjack", style=discord.ButtonStyle.primary)
    async def btn_bj(self, interaction: discord.Interaction, button: ui.Button):
        d = self.bot.get_user(self.user_id)
        d["points"] -= self.amount # Pobieranie punktów w momencie startu gry
        self.bot.save_data()
        
        view = BlackjackGame(self.bot, self.user_id, self.amount)
        embed, wartosc_gracza = view.stworz_embed()
        
        await interaction.response.edit_message(embed=embed, view=view)
        
        # Automatyczne sprawdzenie, czy gracz od razu nie wylosował 21
        if wartosc_gracza == 21:
            await view.stand(interaction, button)

    @ui.button(label="Ruletka", style=discord.ButtonStyle.danger)
    async def btn_roulette(self, interaction: discord.Interaction, button: ui.Button):
        d = self.bot.get_user(self.user_id)
        d["points"] -= self.amount
        self.bot.save_data()
        
        await interaction.response.edit_message(content="🎰 **Losowanie...**", embed=None, view=None)
        await asyncio.sleep(1.5)
        
        if random.random() > 0.50: # Szansa 50/50 na wygraną
            wygrana = self.amount * 2
            d["points"] += wygrana
            res = f"✨ **WYGRANA!** ✨\nTwój zakład: Ruletka (stawka: {self.amount} pkt)\nWynik: +{self.amount} pkt\nNowy stan: `{d['points']:.1f} pkt`"
            kolor = 0x00ff00
        else:
            res = f"💀 **PRZEGRANA** 💀\nTwój zakład: Ruletka (stawka: {self.amount} pkt)\nWynik: -{self.amount} pkt\nNowy stan: `{d['points']:.1f} pkt`"
            kolor = 0xff0000
            
        self.bot.save_data()
        emb = discord.Embed(title="Ruletka | Wynik", description=res, color=kolor)
        emb.set_footer(text=f"Użyj /kasyno aby zagrać ponownie | Dziś o {datetime.now().strftime('%H:%M')}")
        await interaction.edit_original_response(content=None, embed=emb)


class Kasyno(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kasyno", description="Wejdź do kasyna i podwój swoje punkty!")
    async def kasyno(self, interaction: discord.Interaction, stawka: int):
        if stawka < 10: 
            return await interaction.response.send_message("❌ Minimalna stawka to 10 pkt!", ephemeral=True)
            
        d = self.bot.get_user(interaction.user.id)
        if d["points"] < stawka: 
            return await interaction.response.send_message(f"❌ Brak punktów! Masz tylko {d['points']:.1f} pkt.", ephemeral=True)

        embed = discord.Embed(title="Kasyno MAKS REPS", color=0x2b2d31)
        embed.description = "Wybierz gre i sprobuj podwoic swoje punkty!"
        embed.add_field(name="Twoja stawka:", value=f"{stawka} pkt", inline=True)
        embed.add_field(name="Twoje saldo:", value=f"{d['points']:.1f} pkt", inline=True)
        embed.add_field(name="Dostepne gry:", value="**1. Blackjack** | Dobieraj karty, nie przekrocz 21.\nWygrana: x2\n**2. Ruletka** | Szybkie losowanie maszyny (50/50).\nWygrana: x2\n\n*Wygrane i przegrane sa natychmiast rozliczane*", inline=False)
        embed.set_footer(text=f"Dziś o {datetime.now().strftime('%H:%M')}")
        
        view = CasinoMenu(self.bot, interaction.user.id, stawka)
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Kasyno(bot))
