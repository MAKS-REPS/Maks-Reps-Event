import discord
from discord.ext import commands
from google import genai
from google.genai import types
import os

PROMPT_EKSPERTA = """
Jesteś specjalistą AI ds. Kakobuy, ubrań streetwearowych oraz replik (repów) na serwerze Maks Reps.
Twoim głównym zadaniem jest odpowiadanie na pytania o "Best Batch" (BB), kupony oraz pomoc w problemach (gdy coś nie działa) na publicznym kanale czatu.

Twoja oficjalna baza wiedzy o Best Batchach (BB):
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
- ASICS GEL-Kayano 14 / ASICS GEL-NYC -> Batch **ZC** (cena ok. 125-130zł)
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
            print("❌ BŁĄD AI: Brak GEMINI_API_KEY w ai_expert!")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not self.ai_client:
            return

        # Sprawdzenie czy to publiczny kanał z konfiguracji Railway
        normal_channel_env = os.getenv("AI_CHANNEL_ID")
        if not normal_channel_env or message.channel.id != int(normal_channel_env):
            return

        # Sprawdzenie słów kluczowych
        tresc = message.content.lower()
        if not any(slowo in tresc for slowo in SLOWA_KLUCZOWE):
            return

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
                print(f"Błąd publicznego AI: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(AiPublicChat(bot))
