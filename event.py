import discord
from discord.ext import commands
from discord import app_commands, ui
import math
import asyncio
from datetime import datetime, timedelta
import random

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

    @app_commands.command(name="profil", description="Pokazuje statystyki twojego konta")
    async def profil(self, interaction: discord.Interaction):
        d = self.bot.get_user(interaction.user.id)
        pts = d.get("points", 0.0)
        # Obliczanie poziomu (100 pkt = 1 level)
        lvl = min(math.floor(pts / 100) + 1, 50)
        msgs = d.get("msg_count", 0)
        
        embed = discord.Embed(
            title=f"Statystyki użytkownika {interaction.user.name}", 
            color=0x2b2d31
        )
        
        # Avatar po prawej stronie (thumbnail)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        # Pola profilu zgodne ze wzorem
        embed.add_field(name="Level", value=f"**{lvl}**", inline=False)
        embed.add_field(name="Punkty / EXP", value=f"**{pts:.1f}**", inline=False)
        embed.add_field(name="Wiadomości", value=f"**{msgs}**", inline=False)
        
        embed.set_footer(text=f"{NAZWA_EVENTU}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="zadania", description="Lista wszystkich zadań serwerowych")
    async def zadania(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📋 Zadania i Nagrody", 
            description="Wykonaj zadania i zgłoś się po punkty przez `/odbierz`!",
            color=0x3498db
        )
        
        embed.add_field(name="📦 Zamówienie paki", value="Nagroda: **500 pkt**", inline=False)
        embed.add_field(name="🤝 Zamówienie od agenta (z refa)", value="Nagroda: **300 pkt**", inline=False)
        embed.add_field(name="📱 Haul na TikTok/YT (z linkiem DC)", value="Nagroda: **500 pkt**", inline=False)
        embed.add_field(name="🙋 Pomoc innym użytkownikom", value="Nagroda: **10-20 pkt**", inline=False)
        embed.add_field(name="💬 Aktywność na czacie", value="Nagroda: **Level x 1.5 pkt**", inline=False)
        embed.add_field(name="👥 Zaproszenie znajomych (2 os.)", value="Nagroda: **50 pkt**", inline=False)
        
        embed.set_footer(text="Dowody wysyłaj na ticketach!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="odbierz", description="Otwórz ticket, aby odebrać nagrodę")
    async def odbierz(self, interaction: discord.Interaction):
        view = ui.View()
        select = ui.Select(placeholder="Wybierz zadanie do zgłoszenia...")
        
        # Opcje zgłoszeń
        select.add_option(label="Zamówienie paki (500 pkt)", value="Paka", emoji="📦")
        select.add_option(label="Zakup u Agenta (300 pkt)", value="Agent", emoji="🤝")
        select.add_option(label="Social Media Haul (500 pkt)", value="Haul", emoji="📱")
        select.add_option(label="Pomoc innym", value="Pomoc", emoji="🙋")
        select.add_option(label="Zaproszenia / Inne", value="Inne", emoji="✨")
        
        async def callback(inter: discord.Interaction):
            cat = inter.guild.get_channel(TICKET_CATEGORY_ID)
            if not cat:
                return await inter.response.send_message("Błąd: Nie znaleziono kategorii ticketów.", ephemeral=True)
                
            ch = await inter.guild.create_text_channel(
                f"ticket-{inter.user.name}", 
                category=cat,
                reason=f"Zgłoszenie zadania: {select.values[0]}"
            )
            
            emb = discord.Embed(title="Zgłoszenie zadania", color=0x2ecc71)
            emb.description = f"Witaj {inter.user.mention}!\nWybrałeś: **{select.values[0]}**.\n\nPrześlij tutaj dowody (screeny/linki), aby administracja mogła przyznać punkty."
            
            await ch.send(embed=emb)
            await inter.response.send_message(f"Twój ticket został otwarty: {ch.mention}", ephemeral=True)
            
        select.callback = callback
        view.add_item(select)
        await interaction.response.send_message("Wybierz zadanie z listy poniżej:", view=view, ephemeral=True)

    @app_commands.command(name="ranking", description="Top 10 graczy eventu")
    async def ranking(self, interaction: discord.Interaction):
        sorted_users = sorted(self.bot.user_data.items(), key=lambda x: x[1].get('points', 0), reverse=True)[:10]
        
        desc = ""
        for i, (uid, data) in enumerate(sorted_users, 1):
            desc += f"**{i}.** <@{uid}> — `{data.get('points', 0):.1f} pkt`\n"
        
        embed = discord.Embed(title="🏆 Ranking Najlepszych", description=desc if desc else "Brak danych.", color=0xf39c12)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="dailybonus", description="Odbierz swój codzienny bonus punktowy")
    async def daily_bonus(self, interaction: discord.Interaction):
        d = self.bot.get_user(interaction.user.id)
        now = datetime.now()
        last_daily_str = d.get("last_daily")
        
        if last_daily_str:
            last_daily = datetime.fromisoformat(last_daily_str)
            if now < last_daily + timedelta(days=1):
                wait_time = (last_daily + timedelta(days=1)) - now
                h, r = divmod(int(wait_time.total_seconds()), 3600)
                m, _ = divmod(r, 60)
                return await interaction.response.send_message(f"⏳ Bonus dostępny za: **{h}h {m}m**.", ephemeral=True)

        reward = random.randint(15, 30)
        d["points"] += reward
        d["last_daily"] = now.isoformat()
        self.bot.save_data()

        await interaction.response.send_message(f"🎁 Odebrałeś **{reward} pkt** codziennego bonusu!")

async def setup(bot):
    await bot.add_cog(Event(bot))
