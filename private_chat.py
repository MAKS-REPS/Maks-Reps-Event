import discord
from discord import app_commands
from discord.ext import commands
from google import genai
from google.genai import types
import os

PROMPT_EKSPERTA = """
Jesteś prywatnym specjalistą AI ds. Kakobuy, streetwearu i repów na serwerze Maks Reps.
Jesteś na prywatnym kanale, odpowiadaj na WSZYSTKO.

Baza wiedzy o Best Batchach:
- Nike Dunk / Dunk Low -> **M Batch**
- Jordan 1 -> **LJR** (lub **PK 4.0** dla Travisów)
- Jordan 4 -> **GX** (dla Black Cat, Military Black itp.)
- Jordan 3 -> **OG**
- Jordan 11 -> **LJR**
- Air Force 1 -> **XP**
- Yeezy 350 / Slides / Foam Runner / 700 -> **LW**
- New Balance 2002R / 1906 / 550 -> **ZC**
- Balenciaga Track / Speed Trainer -> **OK**
- Balenciaga Runner -> **VG**
- Numeris (Mihara Yasuhiro) -> Batch **W1**
- ASICS GEL-Kayano 14 / NYC -> Batch **ZC**
- Louis Vuitton (LV Skate/Trainer) -> Batch **Foshan** lub **Villian/Pone**

PROMOCOWANIE KUPONÓW:
1. Rejestracja daje kupony: https://ikako.vip/r/maksr3ps
2. Kod -15$: Maks.R3ps
3. Kod -20%: Maks20
Pisz na luzie, krótko i z emotkami.
"""

class ChatCreateView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Otwórz Chat AI", style=discord.ButtonStyle.blurple, custom_id="ai_chat_button")
    async def open_chat(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        
        # Zabezpieczenie: Discord pozwala tylko na MAŁE LITERY w nazwach kanałów
        bezpieczny_nick = user.name.lower().replace(" ", "-")
        channel_name = f"🧠-chat-{bezpieczny_nick}"

        existing_channels = [c for c in guild.channels if c.name == channel_name]
        if len(existing_channels) >= 2:
            return await interaction.response.send_message("❌ Masz już otwarte maksymalnie 2 prywatne kanały!", ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        # Ustawienia widoczności kanału
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        try:
            category = interaction.channel.category
            new_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites, category=category)
            
            welcome_embed = discord.Embed(
                title="🧠 Prywatny Chat AI",
                description=f"Cześć <@{user.id}>!\nZadaj mi dowolne pytanie o repy, wysyłkę lub kupony. \nTutaj odpowiadam na każdą Twoją wiadomość bez słów kluczowych.",
                color=0x5865F2
            )
            await new_channel.send(embed=welcome_embed)
            await interaction.followup.send(f"✅ Stworzono Twój prywatny kanał: <#{new_channel.id}>", ephemeral=True)
            print(f"🎫 Stworzono prywatny kanał dla: {user.name}")
        except discord.errors.Forbidden:
            print("❌ Błąd: Bot nie ma uprawnień do tworzenia kanałów!")
            await interaction.followup.send("❌ Błąd: Bot nie ma odpowiednich uprawnień na serwerze (potrzebuje roli Administrator).", ephemeral=True)

class PrivateChatCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            self.ai_client = genai.Client(api_key=api_key)
        else:
            self.ai_client = None

    async def cog_load(self):
        self.bot.add_view(ChatCreateView())

    @app_commands.command(name="setup_ai_panel", description="Wysyła przycisk z biletami AI")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_ai_panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Prywatny Chat AI",
            description="Kliknij poniżej, aby otworzyć swój ukryty kanał AI.",
            color=0x2f3136
        )
        await interaction.response.send_message(embed=embed, view=ChatCreateView())

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not self.ai_client:
            return

        if not message.channel.name.startswith("🧠-chat-"):
            return

        print(f"💬 [Prywatny Chat] Odpowiadam użytkownikowi {message.author.name}")

        async with message.channel.typing():
            try:
                response = self.ai_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=message.content,
                    config=types.GenerateContentConfig(
                        system_instruction=PROMPT_EKSPERTA,
                        temperature=0.5
                    )
                )
                
                embed = discord.Embed(
                    title="🤖 ASYSTENT AI × MAKS REPS",
                    description=response.text,
                    color=0x5865F2
                )
                await message.reply(embed=embed)
            except Exception as e:
                print(f"❌ Błąd w prywatnym czacie: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(PrivateChatCog(bot))
