import discord
from discord.ext import commands
from google import genai
from google.genai import types
import os

PROMPT_EKSPERTA = """
Jesteś specjalistą AI ds. Kakobuy, ubrań streetwearowych oraz replik (repów) na serwerze Maks Reps.
Twoim zadaniem jest pomoc użytkownikom w problemach, odpowiadanie na podstawowe pytania (np. jak zamawiać, co zrobić gdy coś nie działa) oraz podawanie "Best Batch" (BB) dla butów.

Twoja oficjalna i święta baza wiedzy o Best Batchach (BB):
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

ROZWIĄZYWANIE PROBLEMÓW (Gdy coś nie działa / jest problem):
- Jeśli użytkownik pisze, że coś mu nie działa, ma błąd z płatnością, agentem, stroną lub paczką, odpowiedz mu spokojnie, jak doświadczony kolega. 
- Doradź np. zmianę przeglądarki, sprawdzenie statusu na Kakobuy, upewnienie się czy dobrze wypełnił dane adresowe, lub zasugeruj kontakt z supportem Kakobuy.

PROMOCOWANIE LINKU I KUPONÓW:
Gdy temat dotyczy kuponów, rejestracji, zamawiania lub gdy po prostu pomagasz nowemu użytkownikowi, wspomnij o profitach:
1. Rejestracja z reflinku daje darmowe kupony: https://ikako.vip/r/maksr3ps
2. Kod na -15$ to: Maks.R3ps
3. Kod na -20% to: Maks20

Zasady wysyłek Kakobuy:
- Średnio 1 kg paczki do Polski kosztuje ok. 60-80 PLN (Tax-Free / bezcłowe). Jedzie 10-21 dni.

Zasady zachowania:
- Pisz luźno, po przyjacielsku (jak ziomek z serwera) i używaj emotek (👟, 📦, 🛠️, ⚠️, 💸).
- Odpowiedzi muszą być zwięzłe i na temat.
"""

# Maksymalnie rozbudowana lista słów kluczowych (w tym błędy i podstawy)
SLOWA_KLUCZOWE = [
    "batch", "kakobuy", "wysylka", "wysyłka", "paczka", "rep", "reps", "replik", 
    "jordan", "j4", "j1", "j3", "j11", "dunk", "travis", "wtc", "w2c", "agent", "zamowic", "zamówić",
    "status", "linia", "tax free", "bezclowa", "vouch", "batcha", "batche", "af1", "air force",
    "bb", "best", "numeris", "numerisy", "asics", "asicsy", "kayano", "nyc", "lv", "louis", "skate",
    "yeezy", "slides", "foam", "nb", "new balance", "balenciaga", "track", "runner",
    "kupon", "kupony", "znizka", "zniżka", "znizki", "zniżki", "kod", "kody", "reflink", "link",
    "nie dziala", "nie działa", "blad", "błąd", "problem", "problemy", "help", "pomocy", "pomoc",
    "jak", "co to", "dlaczego", "czemu", "zrobic", "zrobić", "gdzie", "placic", "płacić", "odrzuciło"
]

class AiAutoResponder(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = None
            print("❌ BŁĄD AI: Brak GEMINI_API_KEY!")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        allowed_channel_env = os.getenv("AI_CHANNEL_ID")
        if not allowed_channel_env:
            return
            
        if message.channel.id != int(allowed_channel_env):
            return

        if not self.client:
            return

        # Sprawdzanie całych fraz oraz pojedynczych słów kluczowych
        tresc_wiadomosci = message.content.lower()
        zawiera_slowo_kluczowe = any(slowo in tresc_wiadomosci for slowo in SLOWA_KLUCZOWE)

        if not zawiera_slowo_kluczowe:
            return

        async with message.channel.typing():
            try:
                response = self.client.models.generate_content(
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
                embed.set_footer(text=f"Odpowiedź dla @{message.author.name} • Czat automatyczny AI")
                
                await message.reply(embed=embed)

            except Exception as e:
                print(f"Błąd podczas automatycznego generowania AI: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(AiAutoResponder(bot))
