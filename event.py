import discord
from discord.ext import commands
from discord import app_commands, ui
import math
import asyncio
from datetime import datetime, timedelta
import random

# Konfiguracja
TICKET_CATEGORY_ID = 1486842150661656767
NAZWA_EVENTU = "Maks Reps Event"

class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not self.bot.event_active: return
        
        uid = str(message.author.id)
        d = self.bot.get_user(message.author.id)
        
        # Zliczanie wiadomości do statystyk profilu
        d["msg_count"] = d.get("msg_count", 0) + 1
        
        # System punktów za pisanie (co 5 sekund)
        now = asyncio.get_event_loop().time()
        if now - self.cooldowns.get(uid, 0) > 5:
            d["points"] += 2
            self.cooldowns[uid] = now
            self.bot.save_data()

    @app_commands.command(name="profil", description="Pokazuje szczegółowe statystyki twojego konta")
    async def profil(self, interaction: discord.Interaction):
        d = self.bot.get_user(interaction.user.id)
        pts = d.get("points", 0.0)
        msgs = d.get("msg_count", 0)
        
        lvl = math.floor(pts / 100) + 1
        next_lvl_pts = lvl * 100
        current_lvl_base = (lvl - 1) * 100
        
        progress_pts = pts - current_lvl_base
        percentage = min(max(int(progress_pts), 0), 100)
        
        filled_blocks = percentage // 10
        empty_blocks = 10 - filled_blocks
        progress_bar = "⬜" * filled_blocks + "⬛" * empty_blocks

        sorted_ranking = sorted(self.bot.user_data.items(), key=lambda x: x[1].get('points', 0), reverse=True)
        ranking_pos = "N/A"
        for index, (uid, _) in enumerate(sorted_ranking, 1):
            if uid == str(interaction.user.id):
                ranking_pos = f"#{index}"
                break

        embed = discord.Embed(color=0x2b2d31)
        embed.set_author(name=f"Profil {interaction.user.name}")
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        embed.add_field(name="Level", value=f"{lvl}", inline=False)
        embed.add_field(name="Punkty", value=f"{pts:.1f}", inline=False)
        embed.add_field(name="Ranking", value=f"{ranking_pos}", inline=False)
        embed.add_field(name="Wiadomosci", value=f"{msgs}", inline=False)
        
        embed.add_field(
            name=f"Postep do LVL {lvl + 1}", 
            value=f"[{progress_bar}] **{percentage}%**\n{pts:.1f} / {next_lvl_pts} pkt", 
            inline=False
        )
        
        now = datetime.now().strftime("%H:%M")
        embed.set_footer(text=f"{NAZWA_EVENTU} | Dziś o {now}")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="zadania", description="Lista wszystkich zadań serwerowych")
    async def zadania(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Dostępne zadania", color=0x2b2d31)
        
        tasks = [
            ("📦 1. Zamówienie paki", "WIELORAZOWE | 500 pkt\nZgłoś raz na 24h."),
            ("🔗 2. Rejestracja z linku", "WIELORAZOWE | 50 pkt\nZgłoś raz na 24h."),
            ("👥 3. Zaproszenie 2 osób na serwer", "WIELORAZOWE | 100 pkt\nZgłoś raz na 24h."),
            ("📹 4. Dodaj haula na kanale haule", "WIELORAZOWE | 50-200 pkt\nZgłoś raz na 24h."),
            ("⚠️ 5. Zgłoszenie błędu", "WIELORAZOWE | 30-100 pkt\nZgłoś raz na 24h."),
            ("📢 6. Podesłanie promki", "WIELORAZOWE | 30-100 pkt\nZgłoś raz na 24h."),
            ("🚀 7. Boost serwera", "JEDNORAZOWE | 150 pkt"),
            ("🌐 8. Dodanie linku do dc w bio", "JEDNORAZOWE | 30 pkt"),
            ("🖥️ 9. Zalogowanie na strone", "JEDNORAZOWE | 100 pkt"),
            ("📱 10. Obserwacja na tiktok", "JEDNORAZOWE | 30 pkt"),
            ("📸 11. Obserwacja na instagramie", "JEDNORAZOWE | 30 pkt"),
            ("♠️ 12. Blackjack (w /kasyno)", "Zależne od stawki (Wygrana x2.5)")
        ]

        for name, val in tasks:
            embed.add_field(name=name, value=val, inline=False)
        
        now = datetime.now().strftime("%H:%M")
        embed.set_footer(text=f"{NAZWA_EVENTU} | Dziś o {now}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="odbierz", description="Otwórz ticket, aby zgłosić wykonanie zadania")
    async def odbierz(self, interaction: discord.Interaction):
        view = ui.View()
        select = ui.Select(placeholder="Wybierz zadanie...")
        
        options = [
            ("Zamówienie paczki", "Paka", "📦"),
            ("Rejestracja z linku", "Rejestracja", "🔗"),
            ("Zaproszenie 2 osób", "Zaproszenia", "👥"),
            ("Dodanie haula", "Haul", "📹"),
            ("Zgłoszenie błędu", "Błąd", "⚠️"),
            ("Podesłanie promki", "Promka", "📢"),
            ("Boost serwera", "Boost", "🚀"),
            ("Link dc w bio", "Bio", "🌐"),
            ("Zalogowanie na strone", "Strona", "🖥️"),
            ("Obserwacja Sociali", "Sociale", "📱")
        ]
        
        for label, val, emoji in options:
            select.add_option(label=label, value=val, emoji=emoji)
        
        async def callback(inter: discord.Interaction):
            cat = inter.guild.get_channel(TICKET_CATEGORY_ID)
            if not cat: return await inter.response.send_message("Błąd kategorii ticketów.", ephemeral=True)
                
            ch = await inter.guild.create_text_channel(f"zgloszenie-{inter.user.name}", category=cat)
            
            # Budowanie wiadomości wewnątrz ticketa (na wzór zdjęcia)
            emb = discord.Embed(color=0x3498db) # Niebieski kolor boczny
            
            # Główny napis
            emb.title = "🎫 MAKS REPS × TICKET"
            
            # Treść wiadomości
            selected_category_full = inter.user.name # Domyślnie
            for label, val, _ in options:
                if select.values[0] == val:
                    selected_category_full = label.upper()
                    break

            emb.description = f"Witaj {inter.user.mention}!\n\nWybrałeś kategorię: **{selected_category_full}**.\n\nZaraz ktoś z administracji Ci pomoże."
            
            await ch.send(f"{inter.user.mention}", embed=emb)
            await inter.response.send_message(f"Otwarto ticket: {ch.mention}", ephemeral=True)
            
        select.callback = callback
        view.add_item(select)
        
        emb_main = discord.Embed(title="Zgłoś wykonanie zadania", color=0x2b2d31)
        emb_main.description = "Wybierz zadanie z listy poniżej.\nPo wybraniu zostanie otwarty ticket do weryfikacji.\n\n*Możesz zgłosić jedno zadanie raz na 24h.*"
        
        now = datetime.now().strftime("%H:%M")
        emb_main.set_footer(text=f"{NAZWA_EVENTU} | Dziś o {now}")
        
        await interaction.response.send_message(embed=emb_main, view=view, ephemeral=True)

    @app_commands.command(name="ranking", description="Top 10 graczy eventu")
    async def ranking(self, interaction: discord.Interaction):
        sorted_users = sorted(self.bot.user_data.items(), key=lambda x: x[1].get('points', 0), reverse=True)[:10]
        desc = ""
        for i, (uid, data) in enumerate(sorted_users, 1):
            desc += f"**#{i}** <@{uid}> — **{data.get('points', 0):.1f} pkt**\n"
        
        embed = discord.Embed(title="Ranking TOP 10 eventu", description=desc if desc else "Brak danych.", color=0x2b2d31)
        now = datetime.now().strftime("%H:%M")
        embed.set_footer(text=f"{NAZWA_EVENTU} | Dziś o {now}")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Event(bot))
