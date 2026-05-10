import discord
from discord.ext import commands
from discord import app_commands, ui
import asyncio
from datetime import datetime, date

# --- KONFIGURACJA ---
TICKET_CATEGORY_ID = 1486842150661656767
ALLOWED_CHANNELS = [1468529379318698117, 1457763945631715456]
KOLOR_BIALY = 0xffffff
ADMIN_ROLE_ID = 1457769309735485450  # Rola, która może klikać "Zapisz punkty"

# Progi punktowe dla poziomów
LEVEL_DATA = {
    3: 275, 5: 500, 6: 750, 7: 1000, 9: 1666, 10: 2000, 
    12: 2600, 14: 3200, 15: 3500, 20: 6000, 50: 37500
}

def get_level_info(pts):
    lvl = 1
    for l, p in sorted(LEVEL_DATA.items()):
        if pts >= p: lvl = l
        else: break
    next_lvl_list = [l for l in LEVEL_DATA.keys() if l > lvl]
    next_lvl = min(next_lvl_list) if next_lvl_list else 50
    return lvl, next_lvl, LEVEL_DATA.get(next_lvl, pts)

# --- WIDOK RANKINGU Z PRZYCISKIEM ---
class RankingView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label="Zapisz punkty", style=discord.ButtonStyle.gray, custom_id="save_pts")
    async def save_points(self, interaction: discord.Interaction, button: ui.Button):
        if not any(role.id == ADMIN_ROLE_ID for role in interaction.user.roles):
            return await interaction.response.send_message("❌ Nie masz uprawnień do użycia tego przycisku!", ephemeral=True)

        all_data = "📊 **PEŁNA LISTA PUNKTÓW EVENTOWYCH:**\n\n"
        sorted_users = sorted(self.bot.user_data.items(), key=lambda x: x[1].get('points', 0), reverse=True)
        
        for i, (uid, data) in enumerate(sorted_users, 1):
            pts = data.get('points', 0)
            lvl = get_level_info(pts)[0]
            all_data += f"{i}. <@{uid}> — `{pts:.1f} pkt` (Lvl {lvl})\n"

        try:
            await interaction.user.send(all_data)
            await interaction.response.send_message("✅ Pełna lista punktów została wysłana na Twoje PV!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Nie mogę wysłać Ci wiadomości! Odblokuj wiadomości prywatne.", ephemeral=True)

# --- GŁÓWNA KLASA COG ---
class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not getattr(self.bot, 'event_active', True): return
        if message.channel.id not in ALLOWED_CHANNELS: return
        
        uid = str(message.author.id)
        d = self.bot.get_user(message.author.id)
        d["msg_count"] += 1
        
        now = asyncio.get_event_loop().time()
        if now - self.cooldowns.get(uid, 0) > 5:
            d["points"] += (2 * getattr(self.bot, 'point_multiplier', 1))
            self.cooldowns[uid] = now
            self.bot.save_data()

    @app_commands.command(name="profil", description="Pokazuje twój profil eventowy")
    async def profil(self, interaction: discord.Interaction):
        d = self.bot.get_user(interaction.user.id)
        pts = d["points"]
        lvl, next_lvl, nxt_pts = get_level_info(pts)
        
        progress = min(int((pts / nxt_pts) * 100), 100)
        filled = progress // 10
        bar = "⬛" * filled + "⬜" * (10 - filled)

        sorted_users = sorted(self.bot.user_data.items(), key=lambda x: x[1].get('points', 0), reverse=True)
        rank = next((i for i, (uid, _) in enumerate(sorted_users, 1) if uid == str(interaction.user.id)), "N/A")

        embed = discord.Embed(color=KOLOR_BIALY)
        embed.set_author(name=f"Profil {interaction.user.name}")
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        embed.add_field(name="Level", value=f"**{lvl}**", inline=False)
        embed.add_field(name="Punkty", value=f"**{pts:.1f}**", inline=False)
        embed.add_field(name="Ranking", value=f"**#{rank}**", inline=False)
        embed.add_field(name="Wiadomości", value=f"**{d['msg_count']}**", inline=False)
        embed.add_field(name=f"Postęp do LVL {next_lvl}", value=f"[{bar}] **{progress}%**\n{pts:.1f} / {nxt_pts:.1f} pkt", inline=False)
        
        embed.set_footer(text=f"Maks Reps Event | {datetime.now().strftime('%H:%M')}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ranking", description="Top 10 użytkowników")
    async def ranking(self, interaction: discord.Interaction):
        sorted_u = sorted(self.bot.user_data.items(), key=lambda x: x[1].get('points', 0), reverse=True)[:10]
        
        desc = ""
        for i, (uid, data) in enumerate(sorted_u, 1):
            pts = data.get('points', 0)
            lvl = get_level_info(pts)[0]
            desc += f"**{i}.** <@{uid}> — `{pts:.1f} pkt` (Lvl {lvl})\n"
        
        emb = discord.Embed(title="🏆 Ranking - Maks Reps Event", description=desc or "Brak danych", color=KOLOR_BIALY)
        await interaction.response.send_message(embed=emb, view=RankingView(self.bot))

    @app_commands.command(name="daily", description="Odbierz 15 pkt bonusu")
    async def daily(self, interaction: discord.Interaction):
        d = self.bot.get_user(interaction.user.id)
        if d.get("last_daily") == str(date.today()):
            return await interaction.response.send_message("❌ Już odebrałeś dzisiejszy bonus!", ephemeral=True)
        
        d["points"] += 15
        d["last_daily"] = str(date.today())
        self.bot.save_data()
        await interaction.response.send_message("🎁 Odebrano **15 pkt** bonusu!", ephemeral=True)

    @app_commands.command(name="zadania", description="Lista wszystkich zadań")
    async def zadania(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📝 ZADANIA EVENTOWE", color=KOLOR_BIALY)
        tasks = [
            "1. **Rejestracja z linku**\nWIELORAZOWE | 80 pkt",
            "2. **Zaproszenie 2 osób**\nWIELORAZOWE | 100 pkt",
            "3. **Dodaj haula**\nWIELORAZOWE | 50-200 pkt",
            "4. **Zgłoszenie błędu**\nWIELORAZOWE | 30-100 pkt",
            "5. **Podesłanie promki**\nWIELORAZOWE | 30-100 pkt",
            "6. **Zamówienie paki**\nWIELORAZOWE | 500 pkt",
            "7. **Boost serwera**\nJEDNORAZOWE | 150 pkt",
            "8. **Link w bio**\nJEDNORAZOWE | 30 pkt",
            "9. **Obserwacja TikTok**\nJEDNORAZOWE | 30 pkt",
            "10. **Obserwacja Instagram**\nJEDNORAZOWE | 30 pkt"
        ]
        embed.description = "\n\n".join(tasks)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="odbierz", description="Otwórz ticket po punkty")
    async def odbierz(self, interaction: discord.Interaction):
        options = [
            discord.SelectOption(label="Rejestracja z linku", value="REJESTRACJA", emoji="🔗"),
            discord.SelectOption(label="Zaproszenie 2 osób", value="ZAPROSZENIA", emoji="👥"),
            discord.SelectOption(label="Dodaj haula", value="HAUL", emoji="📹"),
            discord.SelectOption(label="Zgłoszenie błędu", value="BŁĄD", emoji="⚠️"),
            discord.SelectOption(label="Podesłanie promki", value="PROMKA", emoji="📢"),
            discord.SelectOption(label="Zamówienie paki", value="PAKA", emoji="📦"),
            discord.SelectOption(label="Boost serwera", value="BOOST", emoji="🚀"),
            discord.SelectOption(label="Link w bio", value="BIO", emoji="🌐"),
            discord.SelectOption(label="TikTok", value="TIKTOK", emoji="📱"),
            discord.SelectOption(label="Instagram", value="INSTAGRAM", emoji="📸")
        ]

        class TicketView(ui.View):
            @ui.select(placeholder="Wybierz zadanie do odbioru...", options=options)
            async def select_callback(self, inter, select):
                cat = inter.guild.get_channel(TICKET_CATEGORY_ID)
                ch = await inter.guild.create_text_channel(f"zgloszenie-{inter.user.name}", category=cat)
                
                emb = discord.Embed(color=KOLOR_BIALY, title="✨ NOWE ZGŁOSZENIE ✨")
                emb.description = (
                    f"Witaj {inter.user.mention}!\n\n"
                    f"Wybrałeś zadanie: **{select.values[0]}**\n\n"
                    f"> Podeślij tutaj dowód wykonania (screen/link).\n"
                    f"> Administracja sprawdzi zgłoszenie i przyzna punkty! 🛡️"
                )
                emb.set_footer(text="Maks Reps System")
                
                await ch.send(f"{inter.user.mention} | @everyone", embed=emb)
                await inter.response.send_message(f"✅ Ticket otwarty: {ch.mention}", ephemeral=True)

        await interaction.response.send_message("✨ **Jakie zadanie wykonałeś?**", view=TicketView(), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Event(bot))
