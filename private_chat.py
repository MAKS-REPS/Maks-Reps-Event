import discord
from discord import app_commands
from discord.ext import commands
from google import genai
from google.genai import types
import os

PROMPT_PRIVATE = """
Jesteś osobistym, prywatnym doradcą AI na serwerze Maks Reps. Odpowiadasz błyskawicznie, konkretnie i zwięźle. Używaj emotek.
Jeśli użytkownik prześle zdjęcie, zrób szybkie QC: oceń kształt, szwy, jakość, daj ocenę 1-10 i werdykt GL (Green Light) lub RL (Red Light).

TWOJA BAZA WIEDZY:
- Nike Dunk -> M Batch
- Jordan 4 -> GX Batch (Black Cat, Military, Pine Green)
- Jordan 1 -> LJR (PK 4.0 dla modeli Travis Scott)
- Yeezy -> LW Batch
- New Balance / ASICS -> ZC Batch
- Numeris -> W1 | Balenciaga Track -> OK | LV -> Foshan

REFLINK I KUPONY:
- Rejestracja: https://ikako.vip/r/maksr3ps
- Kody: Maks.R3ps (-15$) | Maks20 (-20%)
"""

class TicketAddonsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="👟 Lista Best Batchy", style=discord.ButtonStyle.secondary, custom_id="faq_batche")
    async def faq_batche(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="👟 Oficjalna Lista Best Batchów",
            description="• **Nike Dunk / Dunk Low:** M Batch\n"
                        "• **Jordan 4:** GX Batch\n"
                        "• **Jordan 1:** LJR / PK 4.0\n"
                        "• **Yeezy:** LW Batch\n"
                        "• **ASICS / New Balance:** ZC Batch\n"
                        "• **Numeris:** Batch W1\n"
                        "• **Louis Vuitton:** Foshan\n"
                        "• **Balenciaga (Track):** OK Batch",
            color=0x9b59b6
        )
        await interaction.response.send_message(embed=embed, ephemeral=False)

    @discord.ui.button(label="💸 Kupony i Kody rabatowe", style=discord.ButtonStyle.success, custom_id="faq_kupony")
    async def faq_kupony(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="💸 Kody Rabatowe i Darmowe Kupony",
            description="🎁 [Zarejestruj się klikając tutaj](https://ikako.vip/r/maksr3ps)\n\n"
                        "🔥 **Kody rabatowe:**\n"
                        "• Kod na **-$15**: `Maks.R3ps`\n"
                        "• Kod na **-20%**: `Maks20`",
            color=0x2ecc71
        )
        await interaction.response.send_message(embed=embed, ephemeral=False)


class ChatCreateView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🧠 Zapytaj Eksperta AI (Tekst / QC)", style=discord.ButtonStyle.blurple, custom_id="ai_chat_button_prod")
    async def open_chat(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        
        clean_nick = user.name.lower().replace(" ", "-")
        channel_name = f"🧠-chat-{clean_nick}"

        existing = [c for c in guild.channels if c.name == channel_name]
        if len(existing) >= 1:
            return await interaction.response.send_message("❌ Masz już otwarty swój prywatny kanał AI!", ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        category = interaction.channel.category
        new_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites, category=category)
        
        welcome_embed = discord.Embed(
            title="🧠 Twój Prywatny Ekspert AI",
            description=f"Siemanko <@{user.id}>! Napisz poniżej swoje pytanie lub **użyj komendy `/zapytaj_ai`** aby uzyskać błyskawiczną odpowiedź lub zrobić **QC zdjęcia**!",
            color=0x5865F2
        )
        await new_channel.send(embed=welcome_embed)
        await new_channel.send("⚡ **Szybkie informacje (widoczne dla wszystkich):**", view=TicketAddonsView())
        await interaction.followup.send(f"✅ Twój pokój AI: <#{new_channel.id}>", ephemeral=True)


class PrivateChatCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        api_key = os.getenv("GEMINI_API_KEY")
        self.ai_client = genai.Client(api_key=api_key) if api_key else None

    async def cog_load(self):
        self.bot.add_view(ChatCreateView())
        self.bot.add_view(TicketAddonsView())

    @app_commands.command(name="setup_ai_panel", description="Generuje panel biletów prywatnego AI.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_ai_panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Prywatny Chat AI & System QC",
            description="Kliknij przycisk poniżej, aby otworzyć swój osobisty panel szybkiego wsparcia AI.",
            color=0x2f3136
        )
        await interaction.response.send_message(embed=embed, view=ChatCreateView())

    # 🔥 TA KOMENDA ROZWIĄZUJE PROBLEM: Ma wbudowany bezpiecznik prędkości i obsługę zdjęć
    @app_commands.command(name="zapytaj_ai", description="Zadaj pytanie asystentowi lub prześlij zdjęcie do szybkiego QC.")
    async def zapytaj_ai(self, interaction: discord.Interaction, pytanie: str, zdjecie: discord.Attachment = None):
        if not self.ai_client:
            return await interaction.response.send_message("❌ Błąd konfiguracji API.", ephemeral=True)

        # ⚡ Kluczowe: Mówimy Discordowi, żeby poczekał na bota (brak crashu!)
        await interaction.response.defer(ephemeral=False)

        try:
            contents_payload = []

            if zdjecie:
                if zdjecie.content_type and zdjecie.content_type.startswith("image/"):
                    img_bytes = await zdjecie.read()
                    contents_payload.append(
                        types.Part.from_bytes(data=img_bytes, mime_type=zdjecie.content_type)
                    )
            
            contents_payload.append(types.Part.from_text(text=pytanie))

            response = self.ai_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=contents_payload,
                config=types.GenerateContentConfig(system_instruction=PROMPT_PRIVATE, temperature=0.3)
            )

            title_text = "📸 WYNIK SZYBKIEGO QC" if zdjecie else "🤖 ODPOWIEDŹ AI"
            embed = discord.Embed(title=title_text, description=response.text, color=0x5865F2)
            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(f"❌ [BŁĄD PRIVATE] {e}")
            await interaction.followup.send(f"⚠️ Coś poszło nie tak: `{e}`")

async def setup(bot: commands.Bot):
    await bot.add_cog(PrivateChatCog(bot))
