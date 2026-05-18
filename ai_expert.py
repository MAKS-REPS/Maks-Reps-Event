import discord
from discord.ext import commands
from google import genai
from google.genai import types
import os

PROMPT_EKSPERTA = """
Jesteś specjalistą AI ds. Kakobuy, ubrań streetwearowych oraz replik (repów) na serwerze Maks Reps.
Twoim zadaniem jest odpowiadanie użytkownikom na wszystkie pytania związane z:
1. Zamawianiem przez Kakobuy (jak kupować, jak działa agent, statusy paczek).
2. Repami i ubraniami (jakość batchy, doradzanie najlepszych wersji butów np. Jordan, Dunk, Travis, pomoc w wyborze rozmiaru).
3. Estymacją wysyłek (Znasz przybliżone zasady: np. średnio 1 kg ubrań/butów w wysyłce do Polski kosztuje około 60-80 PLN w zależności od linii, buty z boxem ważą ok. 1.2-1.5kg, bluza ok. 800g, t-shirt ok. 300g. Paczka jedzie zazwyczaj 10-21 dni liniami bezcłowymi / Tax-Free).

Zasady zachowania:
- Odpowiadaj zwięźle, konkretnie i używaj emotek (np. 📦, 👟, ✈️), aby wiadomości były czytelne.
- Pisz w języku polskim, luźnym ale pomocnym tonem (jak ziomek z serwera).
- Jeśli ktoś pyta o rzeczy całkowicie niezwiązane z ubraniami, repami czy Kakobuy, dyplomatycznie przypomnij mu, że jesteś ekspertem od mody i zakupów.
"""

# Lista słów kluczowych. Bot zareaguje na zwykłą wiadomość tylko jeśli zawiera ona choć jedno z tych słów.
SLOWA_KLUCZOWE = [
    "batch", "kakobuy", "wysylka", "wysyłka", "paczka", "rep", "reps", "replik", 
    "jordan", "j4", "j1", "dunk", "travis", "wtc", "w2c", "agent", "zamowic", "zamówić",
    "status", "linia", "tax free", "bezclowa", "bezcłowa", "vouch", "batcha", "batche"
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
        # 1. Ignoruj wiadomości wysłane przez same boty (żeby bot nie rozmawiał sam ze sobą)
        if message.author.bot:
            return

        # 2. BLOKADA KANAŁU: Pobieramy ID dozwolonego kanału z Railway
        allowed_channel_env = os.getenv("AI_CHANNEL_ID")
        if not allowed_channel_env:
            return  # Jeśli nie ustawiłeś kanału w Railway, bot na wszelki wypadek nic nie robi
            
        if message.channel.id != int(allowed_channel_env):
            return  # Jeśli to inny kanał, ignorujemy wiadomość

        if not self.client:
            return

        # 3. SPRAWDZENIE SŁÓW KLUCZOWYCH: Zamieniamy tekst na małe litery, żeby wielkość nie miała znaczenia
        tresc_wiadomosci = message.content.lower()
        zawiera_slowo_kluczowe = any(slowo in tresc_wiadomosci for slowo in SLOWA_KLUCZOWE)

        # Jeśli użytkownik nie pyta o nic z naszej listy tematów, bot milczy
        if not zawiera_slowo_kluczowe:
            return

        # 4. REAKCJA I GENEROWANIE ODPOWIEDZI
        # Uruchamiamy status "typing..." (bot pisze...), żeby użytkownik widział, że AI generuje odpowiedź
        async with message.channel.typing():
            try:
                # Wywołanie modelu Gemini (używamy wersji synchronicznej, bo tak działa domyślnie klient google-genai)
                response = self.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=message.content,
                    config=types.GenerateContentConfig(
                        system_instruction=PROMPT_EKSPERTA,
                        temperature=0.7
                    )
                )
                
                # Budowanie ładnej odpowiedzi w Embedzie
                embed = discord.Embed(
                    title="🤖 ASYSTENT AI × MAKS REPS",
                    description=response.text,
                    color=0x2ecc71 # Zielony kolor dla auto-respondera
                )
                embed.set_footer(text=f"Odpowiedź dla @{message.author.name} • Czat automatyczny AI")
                
                # Odpowiadamy bezpośrednio, oznaczając (pingując) osobę zadającą pytanie
                await message.reply(embed=embed)

            except Exception as e:
                print(f"Błąd podczas automatycznego generowania AI: {e}")
                # W razie błędu nie spamujemy kanału, błąd odłoży się w logach Railway

async def setup(bot: commands.Bot):
    await bot.add_cog(AiAutoResponder(bot))
