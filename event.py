import discord
from discord.ext import commands
from discord import app_commands, ui
import asyncio
import random
from datetime import datetime, date

TICKET_CATEGORY_ID = 1486842150661656767
ALLOWED_CHANNELS = [1468529379318698117, 1457763945631715456]
KOLOR_BIALY = 0xffffff

LEVEL_DATA = {
    3: 275, 5: 500, 6: 750, 7: 1000, 9: 1666, 10: 2000, 
    12: 2600, 14: 3200, 15: 3500, 20: 6000, 50: 37500
}

def get_level_info(pts):
    lvl = 1
    for l, p in sorted(LEVEL_DATA.items()):
        if pts >= p: lvl = l
        else: break
    next_lvl = min([l for l in LEVEL_DATA.keys() if l > lvl] or [50])
    return lvl, next_lvl, LEVEL_DATA.get(next_lvl, pts)

# --- SYSTEM BLACKJACKA ---
def draw_card():
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    suits = ['♠', '♥', '♦', '♣']
    rank = random.choice(ranks)
    suit = random.choice(suits)
    value = 11 if rank == 'A' else (10 if rank in ['J', 'Q', 'K'] else int(rank))
    return f"{rank}{suit}", value

def calc_score(hand):
    score = sum(card[1] for card in hand)
    aces = sum(1 for card in hand if 'A' in card[0])
    while score > 21 and aces > 0:
        score -= 10
        aces -= 1
    return score

class BlackjackView(ui.View):
    def __init__(self, bot, user, bet, p_hand, d_hand):
        super().__init__(timeout=60)
        self.bot = bot
        self.user = user
        self.bet = bet
        self.p_hand = p_hand
        self.d_hand = d_hand
        self.game_over = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("To nie twoja gra!", ephemeral=True)
            return False
        return True

    async def update_board(self, interaction: discord.Interaction):
        p_score = calc_score(self.p_hand)
        d_score = calc_score(self.d_hand)
        
        p_cards_str = " ".join([f"[{c[0]}]" for c in self.p_hand])
        
        if not self.game_over:
            d_cards_str = f"[{self.d_hand[0][0]}] [??]"
            color = KOLOR_BIALY
            title = "Blackjack | Twoja tura"
            desc = f"**Stawka:** {self.bet} pkt\n\n**Krupier:** {d_cards_str}\n**Twoje karty:** {p_cards_str} = {p_score}\n\nDobierz karte lub zostaw.\nCel: Miej wiecej niz krupier, ale nie przekrocz 21"
        else:
            d_cards_str = " ".join([f"[{c[0]}]" for c in self.d_hand])
            d_data = self.bot.get_user(self.user.id)
            
            # Logika wygranej
            if p_score > 21:
                title, color, wynik = "Blackjack | Przegrana", 0xff0000, f"-{self.bet} pkt"
            elif d_score > 21 or p_score > d_score:
                title, color, wynik = "Blackjack | Wygrana!", 0x00ff00, f"+{self.bet} pkt"
                d_data["points"] += (self.bet * 2) # Zwraca stawkę i dodaje wygraną
            elif p_score == d_score:
                title, color, wynik = "Blackjack | Remis", 0xffff00, "0 pkt (zwrot)"
                d_data["points"] += self.bet # Zwraca stawkę
            else:
                title, color, wynik = "Blackjack | Przegrana", 0xff0000, f"-{self.bet} pkt"
                
            self.bot.save_data()
            desc = f"**Twoje karty:** {p_cards_str} = {p_score}\n**Krupier:** {d_cards_str} = {d_score}\n\n**Stawka:** {self.bet} pkt\n**Wynik:** {wynik}"
            
            for child in self.children:
                child.disabled = True

        embed = discord.Embed(title=title, description=desc, color=color)
        embed.set_footer(text=f"Użyj /hazard aby zagrać ponownie | {datetime.now().strftime('%H:%M')}")
        
        if interaction.response.is_done():
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.edit_message(embed=embed, view=self)

    @ui.button(label="Dobierz", style=discord.ButtonStyle.primary)
    async def hit(self, interaction: discord.Interaction, button: ui.Button):
        self.p_hand.append(draw_card())
        if calc_score(self.p_hand) >= 21:
            self.game_over = True
        await self.update_board(interaction)

    @ui.button(label="Stoj", style=discord.ButtonStyle.secondary)
    async def stand(self, interaction: discord.Interaction, button: ui.Button):
        self.game_over = True
        while calc_score(self.d_hand) < 17:
            self.d_hand.append(draw_card())
        await self.update_board(interaction)

# --- MENU KASYNA ---
class CasinoMenu(ui.View):
    def __init__(self, bot, user, bet):
        super().__init__(timeout=60)
        self.bot = bot
        self.user = user
        self.bet = bet

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("To nie twój panel kasyna!", ephemeral=True)
            return False
        return True

    @ui.button(label="Blackjack", style=discord.ButtonStyle.primary)
    async def btn_bj(self, interaction: discord.Interaction, button: ui.Button):
        d = self.bot.get_user(self.user.id)
        d["points"] -= self.bet # Pobieramy stawkę
        self.bot.save_data()
        
        p_hand = [draw_card(), draw_card()]
        d_hand = [draw_card(), draw_card()]
        
        view = BlackjackView(self.bot, self.user, self.bet, p_hand, d_hand)
        if calc_score(p_hand) == 21:
            view.game_over = True # Blackjack z rozdania!
        
        await view.update_board(interaction)

    @ui.button(label="Ruletka", style=discord.ButtonStyle.danger)
    async def btn_roulette(self, interaction: discord.Interaction, button: ui.Button):
        d = self.bot.get_user(self.user.id)
        d["points"] -= self.bet # Pobieramy stawkę
        self.bot.save_data()
        
        await interaction.response.edit_message(content="🎰 **Losowanie...**", embed=None, view=None)
        await asyncio.sleep(1.5)
        
        if random.random() > 0.52:
            wygrana = self.bet * 2
            d["points"] += wygrana
            res = f"✨ **WYGRANA!** ✨\nTwój zakład: Ruletka (stawka: {self.bet} pkt)\nWynik: +{self.bet} pkt\nNowy stan: `{d['points']:.1f} pkt`"
            color = 0x00ff00
        else:
            res = f"💀 **PRZEGRANA** 💀\nTwój zakład: Ruletka (stawka: {self.bet} pkt)\nWynik: -{self.bet} pkt\nNowy stan: `{d['points']:.1f} pkt`"
            color = 0xff0000
            
        self.bot.save_data()
        emb = discord.Embed(title="Ruletka | Wynik", description=res, color=color)
        emb.set_footer(text=f"Użyj /hazard aby zagrać ponownie | {datetime.now().strftime('%H:%M')}")
        await interaction.edit_original_response(content=None, embed=emb)

# --- GŁÓWNA KLASA ---
class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not self.bot.event_active: return
        if message.channel.id not in ALLOWED_CHANNELS: return
        uid = str(message.author.id)
        d = self.bot.get_user(message.author.id)
        d["msg_count"] += 1
        now = asyncio.get_event_loop().time()
        if now - self.cooldowns.get(uid, 0) > 5:
            d["points"] += (2 * getattr(self.bot, 'point_multiplier', 1))
            self.cooldowns[uid] = now
            self.bot.save_data()

    @app_commands.command(name="hazard", description="Wejdź do kasyna i spróbuj podwoić punkty!")
    async def hazard(self, interaction: discord.Interaction, kwota: int):
        d = self.bot.get_user(interaction.user.id)
        if kwota < 10: 
            return await interaction.response.send_message("❌ Minimalna stawka to 10 pkt!", ephemeral=True)
        if d["points"] < kwota: 
            return await interaction.response.send_message(f"❌ Nie masz tylu punktów! Twoje saldo to: {d['points']:.1f} pkt", ephemeral=True)
        
        embed = discord.Embed(title="Kasyno MAKS REPS", color=KOLOR_BIALY)
        embed.description = "Wybierz grę i spróbuj podwoić swoje punkty!"
        embed.add_field(name="Twoja stawka:", value=f"{kwota} pkt", inline=True)
        embed.add_field(name="Twoje saldo:", value=f"{d['points']:.1f} pkt", inline=True)
        embed.add_field(name="Dostępne gry:", value="**1. Blackjack** | Dobieraj karty, nie przekrocz 21.\n**2. Ruletka** | Szybkie losowanie (50/50).\n\n*Wygrane i przegrane są natychmiast rozliczane.*", inline=False)
        embed.set_footer(text=f"Dziś o {datetime.now().strftime('%H:%M')}")
        
        view = CasinoMenu(self.bot, interaction.user, kwota)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="profil", description="Twoje statystyki")
    async def profil(self, interaction: discord.Interaction):
        d = self.bot.get_user(interaction.user.id)
        pts = d["points"]
        lvl, next_lvl, nxt_pts = get_level_info(pts)
        progress = min(int((pts / nxt_pts) * 100), 100)
        bar = "⬛" * (progress // 10) + "⬜" * (10 - (progress // 10))
        sorted_users = sorted(self.bot.user_data.items(), key=lambda x: x[1].get('points', 0), reverse=True)
        rank = next((i for i, (uid, _) in enumerate(sorted_users, 1) if uid == str(interaction.user.id)), "N/A")

        emb = discord.Embed(color=KOLOR_BIALY)
        emb.set_author(name=f"Profil {interaction.user.name}")
        emb.set_thumbnail(url=interaction.user.display_avatar.url)
        emb.add_field(name="Level", value=f"**{lvl}**", inline=False)
        emb.add_field(name="Punkty", value=f"**{pts:.1f}**", inline=False)
        emb.add_field(name="Ranking", value=f"**#{rank}**", inline=False)
        emb.add_field(name="Wiadomości", value=f"**{d['msg_count']}**", inline=False)
        emb.add_field(name=f"Postęp do LVL {next_lvl}", value=f"[{bar}] **{progress}%**\n{pts:.1f} / {nxt_pts:.1f} pkt", inline=False)
        emb.set_footer(text=f"Maks Reps Event | {datetime.now().strftime('%H:%M')}")
        await interaction.response.send_message(embed=emb)

    @app_commands.command(name="daily", description="Odbierz 15 pkt bonusu")
    async def daily(self, interaction: discord.Interaction):
        d = self.bot.get_user(interaction.user.id)
        if d.get("last_daily") == str(date.today()):
            return await interaction.response.send_message("❌ Już odebrałeś dzisiejszy bonus!", ephemeral=True)
        d["points"] += 15
        d["last_daily"] = str(date.today())
        self.bot.save_data()
        await interaction.response.send_message("🎁 Odebrano **15 pkt** bonusu dziennego!", ephemeral=True)

    @app_commands.command(name="ranking", description="Top 10 użytkowników")
    async def ranking(self, interaction: discord.Interaction):
        sorted_u = sorted(self.bot.user_data.items(), key=lambda x: x[1].get('points', 0), reverse=True)[:10]
        desc = ""
        for i, (uid, data) in enumerate(sorted_u, 1):
            desc += f"**#{i}** <@{uid}> - `{data.get('points', 0):.1f} pkt`\n"
        emb = discord.Embed(title="🏆 TOP 10 EVENTU", description=desc or "Brak danych", color=KOLOR_BIALY)
        await interaction.response.send_message(embed=emb)

    @app_commands.command(name="zadania", description="Lista zadań")
    async def zadania(self, interaction: discord.Interaction):
        tasks = [
            "1. **Rejestracja z linku**\nWIELORAZOWE | 80 pkt",
            "2. **Zaproszenie 2 osób na serwer**\nWIELORAZOWE | 100 pkt",
            "3. **Dodaj swojego haula na kanale**\nWIELORAZOWE | 50 - 200 pkt",
            "4. **Zgłoszenie błędu**\nWIELORAZOWE | 30 - 100 pkt",
            "5. **Podesłanie promki**\nWIELORAZOWE | 30 - 100 pkt",
            "6. **Zamówienie paki z mojego linku**\nWIELORAZOWE | 500 pkt",
            "7. **Boost serwera**\nJEDNORAZOWE | 150 pkt",
            "8. **Dodanie linku do discorda w bio**\nJEDNORAZOWE | 30 pkt",
            "9. **Obserwacja na tiktok**\nJEDNORAZOWE | 30 pkt",
            "10. **Obserwacja na instagramie**\nJEDNORAZOWE | 30 pkt"
        ]
        emb = discord.Embed(title="📝 ZADANIA EVENTOWE", description="\n\n".join(tasks), color=KOLOR_BIALY)
        await interaction.response.send_message(embed=emb)

    @app_commands.command(name="odbierz", description="Otwórz ticket po punkty")
    async def odbierz(self, interaction: discord.Interaction):
        options = [
            discord.SelectOption(label="Paka z linku", value="PAKA", emoji="📦"),
            discord.SelectOption(label="Rejestracja", value="REJESTRACJA", emoji="🔗"),
            discord.SelectOption(label="Zaproszenia", value="ZAPROSZENIA", emoji="👥"),
            discord.SelectOption(label="Haul", value="HAUL", emoji="📹"),
            discord.SelectOption(label="Błąd", value="BŁĄD", emoji="⚠️"),
            discord.SelectOption(label="Promka", value="PROMKA", emoji="📢"),
            discord.SelectOption(label="Boost", value="BOOST", emoji="🚀"),
            discord.SelectOption(label="Bio", value="BIO", emoji="🌐"),
            discord.SelectOption(label="Sociale", value="SOCIALE", emoji="📱")
        ]
        class TV(ui.View):
            @ui.select(placeholder="Co wykonałeś?", options=options)
            async def s(self, i, s):
                cat = i.guild.get_channel(TICKET_CATEGORY_ID)
                ch = await i.guild.create_text_channel(f"zgloszenie-{i.user.name}", category=cat)
                e = discord.Embed(title="✨ NOWE ZGŁOSZENIE ✨", color=KOLOR_BIALY, description=f"Kategoria: **{s.values[0]}**\n\nPodeślij dowód, a sprawdzimy go jak najszybciej! 🛡️")
                await ch.send(f"{i.user.mention} | @everyone", embed=e)
                await i.response.send_message(f"✅ Otwarto: {ch.mention}", ephemeral=True)
        await interaction.response.send_message("Wybierz zadanie:", view=TV(), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Event(bot))
