import discord
from discord.ext import commands
from google import genai
from google.genai import types
import os

PROMPT_EKSPERTA = """
Jesteś elitarnym, potężnym asystentem AI ds. streetwearu, mody i replik na serwerze Maks Reps. Jesteś najmądrzejszym botem na świecie w tej dziedzinie.
Masz gigantyczną wiedzę o:
- Rozmiarówkach (sizing: TTS, size up/down) i materiałach.
- Logistyce z Chin (agenci typu Kakobuy, Panda, CSS itp., deklaracje celne, statusy śledzenia, linie Tax Free).
- Historii marek i układaniu outfitów (co do czego pasuje).
- Procesie QC (Quality Check) - na co zwracać uwagę (np. stitching, shape, toebox).

TWOJA ŚWIĘTA I NIEZMIENNA BAZA WIEDZY O "BEST BATCHACH" (BB):
Jeśli ktoś pyta o te konkretne modele, MUSISZ podać te batche:
- Nike Dunk / Dunk Low -> **M Batch**
- Jordan 1 -> **LJR** (lub **PK 4.0** dla modeli Travis Scott)
- Jordan 4 -> **GX** (najlepszy dla Black Cat, Military Black, Pine Green)
- Jordan 3 -> **OG**
- Jordan 11 -> **LJR**
- Air Force 1 -> **XP**
- Yeezy 350 / Slides / Foam Runner / 700 -> **LW**
- New Balance 2002R / 1906 / 550 -> **ZC**
- Balenciaga Track / Speed Trainer -> **OK** | Runner -> **VG**
- Numeris (Mihara Yasuhiro) -> Batch **W1** (cena ok. 180zł)
- ASICS GEL-Kayano 14 / ASICS GEL-NYC -> Batch **ZC** (cena ok. 125-130zł)
- Louis Vuitton (LV Skate / Trainer) -> Batch **Foshan** lub od sprzedawców **Villian / Pone**

ZASADA NR 1: Jeśli ktoś pyta o buty, których NIE MA na liście wyżej, użyj swojej zaawansowanej wiedzy AI, by polecić najlepszy znany Ci batch z rynku (np. PK, OG, PK Kim, H12 itp.) i doradź.
ZASADA NR 2: Zawsze pomagaj w problemach ze stroną (nie działa, jak zamawiać, błędy płatności).

PROMOCOWANIE LINKU I KUPONÓW (Zawsze dodawaj, gdy ktoś pyta o ceny, wysyłkę, pierwsze zamówienie):
1. Rejestracja z tego reflinku daje darmowe kupony: https://ikako.vip/r/maksr3ps
2. Kod na zniżkę -15$: Maks.R3ps
3. Kod na zniżkę -20%: Maks20

Styl wypowiedzi:
Bądź ultra-inteligentny i pomocny, ale pisz luźno, po przyjacielsku (jak doświadczony ziomek z serwera). Używaj emotek (👟, 📦, 💸, 🔥, 🧠). Odpowiadaj zwięźle, bez ścian tekstu.
"""

SLOWA_KLUCZOWE = [
    "batch", "kakobuy", "wysylka", "wysyłka", "paczka", "rep", "reps", "replik", 
    "jordan", "j4", "j1", "j3", "j11", "dunk", "travis", "wtc", "w2c", "agent", "zamowic", "zamówić",
    "status", "linia", "tax free", "bezclowa", "vouch", "batcha", "batche", "af1", "air force",
    "bb", "best", "numeris", "numerisy", "asics", "asicsy", "kayano", "nyc", "lv", "louis", "skate",
    "yeezy", "slides", "foam", "nb", "new balance", "balenciaga", "track", "runner",
    "kupon", "kupony", "znizka", "zniżka", "znizki", "zniżki", "kod", "kody", "reflink", "link",
    "nie dziala", "nie działa", "blad", "błąd", "problem", "help", "pomocy", "rozmiar", "fituje", "celny"
]

class PublicToPrivateView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="💬 Przenieś rozmowę na priv (AI)", style=discord.ButtonStyle.blurple, custom_id="ai_chat_button_prod")
    async def bridge_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

class AiPublicChat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        api_key = os.getenv("GEMINI_API_KEY")
        self.ai_client = genai.Client(api_key=api_key) if api_key else None

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not self.ai_client:
            return

        if message.channel.name.startswith("🧠-chat-"):
            return

        channel_env = os.getenv("AI_CHANNEL_ID")
        if channel_env and message.channel.id != int(channel_env):
            return

        if not any(slowo in message.content.lower() for slowo in SLOWA_KLUCZOWE):
            return

        print(f"💬 [PUBLICZNY] Wykryto słowo kluczowe u @{message.author.name}")
        async with message.channel.typing():
            try:
                response = self.ai_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=message.content,
                    config=types.GenerateContentConfig(system_instruction=PROMPT_EKSPERTA, temperature=0.5)
                )
                
                embed = discord.Embed(title="🤖 ASYSTENT AI × MAKS REPS", description=response.text, color=0x2ecc71)
                embed.set_footer(text=f"Odpowiedź dla @{message.author.name}")
                
                await message.reply(embed=embed, view=PublicToPrivateView())
            except Exception as e:
                print(f"❌ [BŁĄD AI PUBLIC] {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(AiPublicChat(bot))
