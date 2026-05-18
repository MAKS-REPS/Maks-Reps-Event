import discord
from discord import app_commands
from discord.ext import commands
from google import genai
from google.genai import types
import os

PROMPT_EKSPERTA = """
Jesteś prywatnym specjalistą AI ds. Kakobuy, ubrań streetwearowych oraz replik (repów) na serwerze Maks Reps.
Rozmawiasz teraz na prywatnym kanale z użytkownikiem. Pomagaj mu w problemach, doradzaj i podawaj "Best Batch" (BB).

Twoja oficjalna baza wiedzy o Best Batchach (BB):
- Numeris (Mihara Yasuhiro) -> Batch **W1** (cena ok. 180zł)
- ASICS GEL-Kayano 14 / ASICS GEL-NYC -> Batch **ZC** (cena ok. 125-130zł)
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
- Louis Vuitton (LV Skate / Trainer) -> Batch **Foshan** lub **Villian / Pone**

PROMOCOWANIE LINKU I KUPONÓW:
Gdy temat dotyczy kuponów, rejestracji, zamawiania lub gdy po prostu pomagasz nowemu użytkownikowi, wspomnij o profitach:
1. Rejestracja z reflinku daje darmowe kupony: https://ikako.vip/r/maksr3ps
2. Kod na -15$ to: Maks.R3ps
3. Kod na -20% to: Maks20

Zasady zachowania:
- Pisz luźno, po przyjacielsku (jak ziomek z serwera) i używaj emotek (👟, 📦, 💸).
- Odpowiedzi muszą być zwięzłe i konkretne.
"""

# Klasa widoku stałego przycisku (Persistent View)
class ChatCreateView(discord.ui.View):
    def __init__(self, cog_instance):
        super().__init__(timeout=None)
        self.cog_instance = cog_instance

    @discord.ui.button(label="Otwórz Chat AI", style=discord.ButtonStyle.blurple, custom_id="open_ai_chat")
    async def open_chat(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        channel_name = f"🧠-chat-{user.name}"

        # Sprawdzenie limitu kanałów dla użytkownika (max 2)
        existing_channels = [c for c in guild.channels if c.name == channel_name.lower()]
        if len(existing_channels) >= 2:
            return await interaction.response.send_message("❌ Masz już otwarte maksymalnie 2 prywatne kanały AI!", ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        # Nadawanie uprawnień do prywatnego kanału
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        category = interaction.channel.category
        new_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites, category=category)

        welcome_embed = discord.Embed(
            title="🧠 Prywatny Chat AI",
            description=f"Witamy na Twoim prywatnym kanale AI, <@{user.id}>!\n\n"
                        f"• Zadaj mi dowolne pytanie o repy, batche, wysyłkę lub kupony.\n"
                        f"• Pamięć konwersacji działa tylko dla Ciebie.\n"
                        f"• Administratorzy serwera mają wgląd w ten kanał dla zachowania bezpieczeństwa.\n\n"
                        f"*Napisz cokolwiek poniżej, aby zacząć!*",
            color=0x5865F2
        )
        welcome_embed.set_footer(text="Aby zamknąć ten kanał, administrator może go po prostu usunąć.")
        
        await new_channel.send(embed=welcome_embed)
        await interaction.followup.send(f"✅ Twój prywatny kanał został utworzony: <#{new_channel.id}>", ephemeral=True)

# Klasa Rozszerzenia (Cog)
class PrivateChatCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            self.ai_client = genai.Client(api_key=api_key)
        else:
            self.ai_client = None
            print("❌ BŁĄD AI: Brak GEMINI_API_KEY w zmiennych!")

    # Rejestrujemy przycisk podczas ładowania modułu, by działał po restarcie bota
    async def cog_load(self):
        self.bot.add_view(ChatCreateView(self))

    # Komenda slash do wysłania wiadomości z przyciskiem panelu
    @app_commands.command(name="setup_ai_panel", description="Wysyła panel z przyciskiem do tworzenia prywatnych czatów AI.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_ai_panel(interaction: discord.Interaction):
        embed = discord.Embed(
            title="Prywatny Chat AI",
            description="Kliknij przycisk poniżej, aby otworzyć **swój prywatny kanał AI**.\n"
                        "• Max **2** kanały na osobę\n"
                        "• Pamięć konwersacji tylko dla Ciebie\n"
                        "• Auto-usuwanie po dłuższej nieaktywności (manualne przez admina)",
            color=0x2f3136
        )
        view = ChatCreateView(self)
        await interaction.response.send_message(embed=embed, view=view)

    # Nasłuchiwanie wiadomości na utworzonych kanałach prywatnych
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        # Sprawdzenie czy kanał zaczyna się od prefixu prywatnego czatu bota
        if not message.channel.name.startswith("🧠-chat-"):
            return

        if not self.ai_client:
            return

        # Bot odpowiada na absolutnie każdą wiadomość wewnątrz tego specjalnego kanału
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
                embed.set_footer(text=f"Prywatna rozmowa z @{message.author.name}")
                
                await message.reply(embed=embed)

            except Exception as e:
                print(f"Błąd generowania AI na kanale prywatnym: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(PrivateChatCog(bot))
