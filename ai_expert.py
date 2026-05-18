import discord
from discord.ext import commands
from google import genai
from google.genai import types
import os

PROMPT_PUBLICZNY = """
Jesteś najszybszym i najmądrzejszym asystentem modowym serwera Maks Reps. Odpowiadasz krótko, na temat, w 2-3 zdaniach. Używaj emotek.

ŚWIĘTA BAZA BATCHY:
- Nike Dunk -> M Batch
- Jordan 1 -> LJR (PK 4.0 dla Travis Scott)
- Jordan 4 -> GX Batch (Najlepszy na Black Cat, Military, Pine Green)
- Yeezy -> LW Batch
- New Balance / ASICS -> ZC Batch

KUPONY:
- Reflink: https://ikako.vip/r/maksr3ps
- Kody: Maks.R3ps | Maks20
"""

SLOWA_KLUCZOWE = ["j1", "j4", "dunk", "travis", "batch", "batcha", "batche", "kakobuy", "kupon", "kupony", "yeezy", "qc"]

class AiPublicChat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        api_key = os.getenv("GEMINI_API_KEY")
        self.ai_client = genai.Client(api_key=api_key) if api_key else None

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not self.ai_client:
            return

        # Ignoruj prywatne pokoje czatowe AI, tam działa osobna komenda
        if message.channel.name.startswith("🧠-chat-"):
            return

        # Sprawdzenie słów kluczowych
        if not any(slowo in message.content.lower() for slowo in SLOWA_KLUCZOWE):
            return

        print(f"💬 [PUBLIC] Wykryto słowo kluczowe w: '{message.content}'")

        async with message.channel.typing():
            try:
                response = self.ai_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=message.content,
                    config=types.GenerateContentConfig(system_instruction=PROMPT_PUBLICZNY, temperature=0.2)
                )
                
                embed = discord.Embed(title="🤖 SZYBKI EKSPERT AI", description=response.text, color=0x2ecc71)
                embed.set_footer(text=f"Odpowiedź dla @{message.author.name}")
                await message.reply(embed=embed)
                
            except Exception as e:
                print(f"❌ [BŁĄD PUBLIC] {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(AiPublicChat(bot))
