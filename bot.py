import discord
from discord import app_commands
from discord.ext import commands
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = os.getenv('GUILD_ID')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

PROMPT_EKSPERTA = """
Jesteś specjalistą AI ds. Kakobuy, ubrań streetwearowych oraz replik (repów) na serwerze Maks Reps.
Twoim zadaniem jest odpowiadanie na pytania o "Best Batch" (BB), kupony oraz pomoc w problemach (gdy coś nie działa).

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
Gdy temat dotyczy kuponów, rejestracji, zamawiania lub pomocy, podaj te dane:
1. Rejestracja z reflinku daje darmowe kupony: https://ikako.vip/r/maksr3ps
2. Kod na -15$ to: Maks.R3ps
3. Kod na -20% to: Maks20

Zasady zachowania:
- Pisz luźno, po przyjacielsku (jak ziomek z serwera) i używaj emotek (👟, 📦, 💸).
- Odpowiedzi muszą być zwięzłe i konkretne.
"""

# Słowa kluczowe dla kanału publicznego (normalnego chatu)
SLOWA_KLUCZOWE = [
    "batch", "kakobuy", "wysylka", "wysyłka", "paczka", "rep", "reps", "replik", 
    "jordan", "j4", "j1", "j3", "j11", "dunk", "travis", "wtc", "w2c", "agent", "zamowic", "zamówić",
    "status", "linia", "tax free", "bezclowa", "vouch", "batcha", "batche", "af1", "air force",
    "bb", "best", "numeris", "numerisy", "asics", "asicsy", "kayano", "nyc", "lv", "louis", "skate",
    "yeezy", "slides", "foam", "nb", "new balance", "balenciaga", "track", "runner",
    "kupon", "kupony", "znizka", "zniżka", "znizki", "zniżki", "kod", "kody", "reflink", "link",
    "nie dziala", "nie działa", "blad", "błąd", "problem", "help", "pomocy"
]

# Klasa widoku przycisku do otwierania prywatnych chatów
class ChatCreateView(discord.ui.View):
    def __init__(self, bot_instance):
        super().__init__(timeout=None)
        self.bot_instance = bot_instance

    @discord.ui.button(label="Otwórz Chat AI", style=discord.ButtonStyle.blurple, custom_id="open_ai_chat")
    async def open_chat(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        channel_name = f"🧠-chat-{user.name}"

        existing_channels = [c for c in guild.channels if c.name == channel_name.lower()]
        if len(existing_channels) >= 2:
            return await interaction.response.send_message("❌ Masz już otwarte maksymalnie 2 prywatne kanały AI!", ephemeral=True)

        await interaction.response.defer(ephemeral=True)

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
                        f"• Tutaj odpowiadam na **każdą** Twoją wiadomość (nie musisz trafiać w słowa kluczowe).\n"
                        f"• Pamięć konwersacji działa tylko dla Ciebie.\n"
                        f"• Admini mają wgląd w ten kanał dla bezpieczeństwa.\n\n"
                        f"*Zadaj swoje pytanie poniżej!*",
            color=0x5865F2
        )
        await new_channel.send(embed=welcome_embed)
        await interaction.followup.send(f"✅ Twój prywatny kanał został utworzony: <#{new_channel.id}>", ephemeral=True)


class GłównyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)
        if GEMINI_API_KEY:
            self.ai_client = genai.Client(api_key=GEMINI_API_KEY)
        else:
            self.ai_client = None
            print("❌ BŁĄD AI: Brak GEMINI_API_KEY!")

    async def setup_hook(self):
        # Rejestrujemy widok przycisku, żeby działał po restarcie bota
        self.add_view(ChatCreateView(self))
        
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            print(f"✅ Komendy zsynchronizowane dla serwera: {GUILD_ID}")
        else:
            await self.tree.sync()

bot = GłównyBot()

@bot.event
async def on_ready():
    print(f"🚀 Połączony Bot AI (Wszystko w jednym pliku) działa! Zalogowano jako {bot.user}")


# KOMENDA DO TWORZENIA PANELU Z PRZYCISKIEM
@bot.tree.command(name="setup_ai_panel", description="Wysyła panel z przyciskiem do tworzenia prywatnych czatów AI.")
@app_commands.checks.has_permissions(administrator=True)
async def setup_ai_panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Prywatny Chat AI",
        description="Kliknij przycisk poniżej, aby otworzyć **swój prywatny kanał AI**.\n"
                    "• Max **2** kanały na osobę\n"
                    "• Pamięć konwersacji tylko dla Ciebie\n"
                    "• Wgląd dla administracji",
        color=0x2f3136
    )
    view = ChatCreateView(bot)
    await interaction.response.send_message(embed=embed, view=view)


# OBSŁUGA CZATU (PUBLICZNEGO I PRYWATNEGO KANAŁU)
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if not bot.ai_client:
        return

    is_private_chat = message.channel.name.startswith("🧠-chat-")
    
    # Pobieramy ID publicznego kanału z Railway
    normal_channel_env = os.getenv("AI_CHANNEL_ID")
    is_normal_chat = normal_channel_env and message.channel.id == int(normal_channel_env)

    # Jeśli to nie jest kanał prywatny ani wyznaczony publiczny -> ignoruj
    if not is_private_chat and not is_normal_chat:
        return

    # Na publicznym sprawdzamy słowa kluczowe. Na prywatnym odpowiadamy na wszystko.
    if is_normal_chat:
        tresc = message.content.lower()
        if not any(slowo in tresc for slowo in SLOWA_KLUCZOWE):
            return

    # Generowanie odpowiedzi przez AI
    async with message.channel.typing():
        try:
            response = bot.ai_client.models.generate_content(
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
                color=0x5865F2 if is_private_chat else 0x2ecc71
            )
            embed.set_footer(text=f"Odpowiedź dla @{message.author.name} • {'Prywatny Chat' if is_private_chat else 'Publiczny Chat'}")
            
            await message.reply(embed=embed)

        except Exception as e:
            print(f"Błąd AI: {e}")


if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ Brak TOKENU bota w zmiennych Railway!")
