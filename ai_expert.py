import discord
from discord import app_commands
from discord.ext import commands
from google import genai
from google.genai import types
import os

# Definiujemy instrukcję systemową – tutaj programujemy "mózg" bota, jego wiedzę o Kakobuy i repach
PROMPT_EKSPERTA = """
Jesteś specjalistą AI ds. Kakobuy, ubrań streetwearowych oraz replik (repów) na serwerze Maks Reps.
Twoim zadaniem jest odpowiadanie użytkownikom na wszystkie pytania związane z:
1. Zamawianiem przez Kakobuy (jak kupować, jak działa agent, statusy paczek).
2. Repami i ubraniami (jakość batchy, doradzanie najlepszych wersji butów np. Jordan, Dunk, Travis, pomoc w wyborze rozmiaru).
3. Estymacją wysyłek (Znasz przybliżone zasady: np. średnio 1 kg ubrań/butów w wysyłce do Polski kosztuje około 60-80 PLN w zależności od linii, buty z boxem ważą ok. 1.2-1.5kg, bluza ok. 800g, t-shirt ok. 300g. Paczka jedzie zazwyczaj 10-21 dni liniami bezcłowymi / Tax-Free).

Zasady zachowania:
- Odpowiadaj zwięźle, konkretnie i używaj emotek (np. 📦, 👟, ✈️), aby wiadomości były czytelne.
- Pisz w języku polskim, luźnym ale pomocnym tonem (jak ziomek z serwera).
- Jeśli ktoś pyta o rzeczy całkowicie niezwiązane z ubraniami, repami czy Kakobuy, dyplomatycznie przypomnij mu, że jesteś ekspertem od mody i zakupów i chętnie pomożesz w tym temacie.
"""

class AiExpert(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Inicjalizacja klienta Gemini przy użyciu oficjalnej biblioteki google-genai
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = None
            print("❌ BŁĄD AI: Brak GEMINI_API_KEY w pliku .env! Moduł AI nie będzie działać.")

    @app_commands.command(name="ai", description="Zadaj pytanie asystentowi ds. Kakobuy, repów i wysyłek!")
    @app_commands.describe(pytanie="Wpisz swoje pytanie (np. Ile idzie paczka? Jaki batch na Jordany 4?)")
    async def ai_ask(self, interaction: discord.Interaction, pytanie: str):
        if not self.client:
            return await interaction.response.send_message("❌ Funkcja AI jest obecnie niedostępna (brak konfiguracji API).", ephemeral=True)

        # Informujemy użytkownika i Discorda, że bot "myśli" (generowanie odpowiedzi może zająć 1-3 sekundy)
        await interaction.response.defer()

        try:
            # Wywołanie modelu Gemini 2.5 Flash z instrukcją systemową
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=pytanie,
                config=types.GenerateContentConfig(
                    system_instruction=PROMPT_EKSPERTA,
                    temperature=0.7 # Odpowiednia elastyczność i kreatywność
                )
            )
            
            # Składamy odpowiedź w ładny Embed
            embed = discord.Embed(
                title="🤖 ASYSTENT AI × MAKS REPS",
                description=response.text,
                color=0x3498db
            )
            embed.add_field(name="❓ Twoje pytanie:", value=f"*{pytanie}*", inline=False)
            embed.set_footer(text="Odpowiedzi generowane automatycznie przez AI. Zawsze weryfikuj ważne informacje na poradnikach.")
            
            # Wysyłamy gotową odpowiedź
            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(f"Błąd podczas generowania odpowiedzi AI: {e}")
            await interaction.followup.send("❌ Wystąpił błąd podczas przetwarzania pytania przez AI. Spróbuj ponownie później.")

async def setup(bot: commands.Bot):
    await bot.add_cog(AiExpert(bot))
