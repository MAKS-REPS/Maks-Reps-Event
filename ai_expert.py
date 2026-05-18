import discord
from discord.ext import commands
from google import genai
from google.genai import types
import os

PROMPT_EKSPERTA = """
Jesteś specjalistą AI ds. Kakobuy, streetwearu i repów na serwerze Maks Reps. Pomagaj z problemami i podawaj "Best Batch" (BB).

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
- Numeris (Mihara Yasuhiro) -> Batch **W1** (cena ok. 180zł)
- ASICS GEL-Kayano 14 / NYC -> Batch **ZC** (cena ok. 125-130zł)
- Louis Vuitton (LV Skate/Trainer) -> Batch **Foshan** lub **Villian / Pone**

PROMOCOWANIE LINKU I KUPONÓW (ZAWSZE GDY KTOŚ PYTA O ZNIŻKI):
1. Darmowe kupony za rejestrację: https://ikako.vip/r/maksr3ps
2. Kod -15$: Maks.R3ps
3. Kod -20%: Maks20
Pisz luźno, używaj emotek.
"""

SLOWA_KLUCZOWE = [
    "batch", "kakobuy", "wysylka", "wysyłka", "paczka", "rep", "reps", "replik", 
    "jordan", "j4", "j1", "j3", "j11", "dunk", "travis", "wtc", "w2c", "agent", "zamowic", "zamówić",
    "status", "linia", "tax free", "bezclowa", "vouch", "batcha", "batche", "af1", "air force",
    "bb", "best", "numeris", "numerisy", "asics", "asicsy", "kayano", "nyc", "lv", "louis", "skate",
    "yeezy", "slides", "foam", "nb", "new balance", "balenciaga", "track", "runner",
    "kupon", "kupony", "znizka", "zniżka", "znizki", "zniżki", "kod", "kody", "reflink", "link",
    "nie dziala", "nie działa", "blad", "błąd", "problem", "help", "pomocy"
]

class AiPublicChat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            self.ai_client = genai.Client(api_key=api_key)
        else:
            self.ai_client = None
            print("❌ BŁĄD: Brak GEMINI_API_KEY w ustawieniach Railway!")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not self.ai_client:
            return

        # Zabezpieczenie, żeby bot nie odpowiadał podwójnie na kanale prywatnym
        if message.channel.name.startswith("🧠-chat-"):
            return

        # Sprawdzenie kanału publicznego
        channel_env = os.getenv("AI_CHANNEL_ID")
        if channel_env:
            try:
                if message.channel.id != int(channel_env):
                    return
            except ValueError:
                pass

        # Sprawdzanie słów kluczowych
        tresc = message.content.lower()
        if not any(slowo in tresc for slowo in SLOWA_KLUCZOWE):
            return

        print(f"💬 [Zwykły Chat] Wykryto słowo kluczowe od użytkownika: {message.author.name}")

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
                    color=0x2ecc71
                )
                embed.set_footer(text=f"Odpowiedź dla @{message.author.name} • Publiczny Chat")
                await message.reply(embed=embed)
            except Exception as e:
                print(f"❌ BŁĄD łączenia z AI: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(AiPublicChat(bot))
