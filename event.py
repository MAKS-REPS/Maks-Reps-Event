import discord
from discord.ext import commands
from discord import app_commands, ui
import math
import asyncio

TICKET_CATEGORY_ID = 1486842150661656767
NAZWA_EVENTU = "Maks Reps Event"

class TicketControl(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @ui.button(label="🔒 Zamknij", style=discord.ButtonStyle.danger)
    async def close(self, interaction, button):
        await interaction.response.send_message("Usuwanie kanału...")
        await asyncio.sleep(3)
        await interaction.channel.delete()

class TaskSelect(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Zamówienie paki z linku", emoji="📦"),
            discord.SelectOption(label="Obserwacja na TikToku", emoji="📱"),
            discord.SelectOption(label="Zaproszenie 2 osób", emoji="👥"),
            discord.SelectOption(label="Dodanie haula", emoji="🎥")
        ]
        super().__init__(placeholder="Wybierz zadanie...", options=options)

    async def callback(self, interaction):
        cat = interaction.guild.get_channel(TICKET_CATEGORY_ID)
        ch = await interaction.guild.create_text_channel(f"ticket-{interaction.user.name}", category=cat)
        embed = discord.Embed(title="Weryfikacja Zadania", description=f"Użytkownik: {interaction.user.mention}\nZadanie: **{self.values[0]}**", color=0x2ecc71)
        await ch.send(embed=embed, view=TicketControl())
        await interaction.response.send_message(f"Otwarto ticket: {ch.mention}", ephemeral=True)

class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not self.bot.event_active: return
        uid = str(message.author.id)
        now = asyncio.get_event_loop().time()
        if now - self.cooldowns.get(uid, 0) > 5:
            d = self.bot.get_user(uid)
            d["points"] += 2
            self.cooldowns[uid] = now
            self.bot.save_data()

    @app_commands.command(name="level")
    async def level(self, interaction):
        d = self.bot.get_user(interaction.user.id)
        lvl = min(math.floor(d["points"] / 100) + 1, 50)
        embed = discord.Embed(title=f"Profil {interaction.user.name}", color=0xf1c40f)
        embed.add_field(name="Level", value=str(lvl))
        embed.add_field(name="Punkty", value=str(d["points"]))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="zadania")
    async def zadania(self, interaction):
        embed = discord.Embed(title="Zadania", description="1. Paka z linku (100 pkt)\n2. TikTok (30 pkt)\n3. Zaproszenia (100 pkt)", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="odbierz")
    async def odbierz(self, interaction):
        view = ui.View(); view.add_item(TaskSelect())
        await interaction.response.send_message("Wybierz zadanie do zweryfikowania:", view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Event(bot))
