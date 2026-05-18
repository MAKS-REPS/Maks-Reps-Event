import discord
from discord import app_commands
from discord.ext import commands
from google import genai
from google.genai import types
import os
import io

PROMPT_EKSPERTA_PRIVATE = """
Jesteś osobistym, prywatnym doradcą AI na serwerze Maks Reps. Jesteś najbardziej zaawansowanym botem modowym na świecie.
Rozmawiasz na prywatnym kanale 1-na-1. Masz potężną wiedzę ogólną o:
- Wyborze odpowiednich ubrań i składaniu outfitów (możesz działać jak osobisty stylista).
- Rozmiarówkach butów i ubrań (co fituje True To Size, gdzie trzeba zrobić size up).
- Tłumaczeniu statusów przesyłek z Chin, cłach, deklaracjach i procesie wysyłki (Kakobuy, inni agenci).
- Jakości replik, wyłapywaniu wad na zdjęciach (flaws, stitching, shape).

TWOJA OFICJALNA BAZA "BEST BATCHÓW" (Zawsze się jej trzymaj):
- Nike Dunk / Dunk Low -> **M Batch**
- Jordan 1 -> **LJR** (lub **PK 4.0** dla modeli Travis Scott)
- Jordan 4 -> **GX** (najlepszy dla Black Cat, Military, Pine Green)
- Jordan 3 -> **OG** | Jordan 11 -> **LJR** | Air Force 1 -> **XP**
- Yeezy (wszystkie modele) -> **LW**
- New Balance (2002R/1906/550) -> **ZC** | ASICS -> **ZC**
- Numeris -> **W1** | Balenciaga Track -> **OK** | Balenciaga Runner -> **VG**
- Louis Vuitton -> **Foshan** lub **Villian/Pone**

Dla butów spoza tej listy - użyj swojej ogólnej wiedzy AI, by doradzić najlepszy batch dostępny na rynku.

KUPONY (Przypominaj o nich dyskretnie przy tematach zakupowych):
1. Zarejestruj się by zgarnąć darmowe kupony: https://ikako.vip/r/maksr3ps
2. Kod -15$: Maks.R3ps
3. Kod -20%: Maks20

Pamiętasz całą historię rozmowy. Bądź niezwykle inteligentny, pomocny, ale rozmawiaj na luzie, jak starszy ziomek z serwera. Używaj emotek.
"""

class TicketAddonsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="👟 Lista Best Batchy", style=discord.ButtonStyle.secondary, custom_id="faq_batche")
    async def faq_batche(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="👟 Oficjalna Lista Best Batchów",
            description="• **Nike Dunk / Dunk Low:** M Batch\n"
                        "• **Jordan 4:** GX Batch (Black Cat, Military, Pine Green)\n"
                        "• **Jordan 1:** LJR / PK 4.0 (Najlepsze dla Travisów)\n"
                        "• **Yeezy (350, Slides, Foam):** LW Batch\n"
                        "• **ASICS (Kayano 14, NYC) / New Balance:** ZC Batch\n"
                        "• **Numeris (Mihara):** Batch W1\n"
                        "• **Louis Vuitton (Skate/Trainer):** Foshan / Villian\n"
                        "• **Balenciaga (Track):** OK Batch | **(Runner):** VG Batch",
            color=0x9b59b6
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="💸 Kupony i Kody rabatowe", style=discord.ButtonStyle.success, custom_id="faq_kupony")
    async def faq_kupony(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="💸 Kody Rabatowe i Darmowe Kupony",
            description="🎁 **Pakiet Kuponów za Rejestrację:**\n[Zarejestruj się klikając tutaj](https://ikako.vip/r/maksr3ps)\n\n"
                        "🔥 **Dodatkowe kody rabatowe do wpisania:**\n"
                        "• Kod na **-$15**: `Maks.R3ps`\n"
                        "• Kod na **-20%**: `Maks20`",
            color=0x2ecc71
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


class ChatCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Zamknij i usuń chat", style=discord.ButtonStyle.danger, custom_id="close_ai_chat")
    async def close_chat(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⚙️ Trwa generowanie transkrypcji i usuwanie kanału...", ephemeral=False)
        
        channel = interaction.channel
        guild = interaction.guild
        user_name = channel.name.replace("🧠-chat-", "")
        
        transcript_text = f"=== TRANSKRYPCJA CZATU AI DLA UŻYTKOWNIKA: {user_name.upper()} ===\n\n"
        async for msg in channel.history(limit=100, oldest_first=True):
            if msg.embeds and "Twój Prywatny Ekspert AI" in (msg.embeds[0].title or ""):
                continue
            
            author = "BOT (AI)" if msg.author.bot else f"UŻYTKOWNIK (@{msg.author.name})"
            content = msg.embeds[0].description if (msg.author.bot and msg.embeds) else msg.content
            transcript_text += f"[{msg.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {author}: {content}\n\n"
            
        transcript_text += "=== KONIEC TRANSKRYPCJI ==="
        
        log_channel_id = os.getenv("AI_LOG_CHANNEL_ID")
        if log_channel_id:
            try:
                log_channel = guild.get_channel(int(log_channel_id))
                if log_channel:
                    file_stream = io.BytesIO(transcript_text.encode('utf-8'))
                    discord_file = discord.File(fp=file_stream, filename=f"chat-{user_name}.txt")
                    
                    log_embed = discord.Embed(
                        title="🔒 Zamknięto Chat AI",
                        description=f"Opiekun czatu: <@{interaction.user.id}>\nKlient: **{user_name}**\nPoniżej znajduje się pełny zapis rozmowy ze sztuczną inteligencją.",
                        color=0xe74c3c
                    )
                    await log_channel.send(embed=log_embed, file=discord_file)
            except Exception as e:
                print(f"❌ [LOGI ERROR] Nie udało się wysłać transkrypcji: {e}")

        import asyncio
        await asyncio.sleep(2)
        await channel.delete()


class ChatCreateView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Otwórz Chat AI", style=discord.ButtonStyle.blurple, custom_id="ai_chat_button_prod")
    async def open_chat(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        
        clean_nick = user.name.lower().replace(" ", "-")
        channel_name = f"🧠-chat-{clean_nick}"

        existing = [c for c in guild.channels if c.name == channel_name]
        if len(existing) >= 2:
            return await interaction.response.send_message("❌ Masz już otwarte maksymalnie 2 prywatne kanały AI!", ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        try:
            category = interaction.channel.category
            new_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites, category=category)
            
            welcome_embed = discord.Embed(
                title="🧠 Twój Prywatny Ekspert AI",
                description=f"Siemanko <@{user.id}>! Trafiłeś do prywatnego pokoju rozmów z AI.\n\n"
                            f"• Jestem tu, aby pomóc Ci we wszystkim – od wyboru idealnego batcha, po pomoc z agentem.\n"
                            f"• Znam się na fitach, rozmiarówkach i wysyłce.\n"
                            f"• Możesz też użyć przycisków poniżej po szybkie odpowiedzi.",
                color=0x5865F2
            )
            welcome_embed.set_footer(text="Rozmowy są archiwizowane i monitorowane przez administrację.")
            
            await new_channel.send(embed=welcome_embed, view=ChatCloseView())
            await new_channel.send("⚡ **Szybkie akcje (FAQ bez czekania):**", view=TicketAddonsView())
            
            await interaction.followup.send(f"✅ Twój prywatny czat AI został wygenerowany: <#{new_channel.id}>", ephemeral=True)
        except discord.errors.Forbidden:
            await interaction.followup.send("❌ Bot nie ma uprawnień (Administratora) do tworzenia kanałów!", ephemeral=True)


class PrivateChatCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        api_key = os.getenv("GEMINI_API_KEY")
        self.ai_client = genai.Client(api_key=api_key) if api_key else None

    async def cog_load(self):
        self.bot.add_view(ChatCreateView())
        self.bot.add_view(ChatCloseView())
        self.bot.add_view(TicketAddonsView())

    @app_commands.command(name="setup_ai_panel", description="Generuje oficjalny panel biletów prywatnego AI.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_ai_panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Prywatny Chat AI",
            description="Kliknij przycisk poniżej, aby otworzyć **swój prywatny kanał AI**.\n\n"
                        "• Najmądrzejsze wsparcie modowe i techniczne\n"
                        "• Szybkie przyciski FAQ w środku\n"
                        "• Pełne wsparcie logistyczne",
            color=0x2f3136
        )
        await interaction.response.send_message(embed=embed, view=ChatCreateView())

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not self.ai_client:
            return

        if not message.channel.name.startswith("🧠-chat-"):
            return

        if message.content.startswith("⚡ **Szybkie akcje"):
            return

        print(f"🧠 [PRYWATNY] Budowanie kontekstu rozmowy dla @{message.author.name}...")
        async with message.channel.typing():
            try:
                history_contents = []
                async for msg in message.channel.history(limit=15, oldest_first=True):
                    if msg.embeds and "Twój Prywatny Ekspert AI" in (msg.embeds[0].title or ""):
                        continue
                    if msg.content.startswith("⚡ **Szybkie akcje"):
                        continue
                        
                    if msg.author.bot:
                        bot_text = msg.embeds[0].description if msg.embeds else msg.content
                        history_contents.append(types.Content(role="model", parts=[types.Part.from_text(text=bot_text)]))
                    else:
                        history_contents.append(types.Content(role="user", parts=[types.Part.from_text(text=msg.content)]))

                if not history_contents or history_contents[-1].role != "user":
                    history_contents.append(types.Content(role="user", parts=[types.Part.from_text(text=message.content)]))

                response = self.ai_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=history_contents,
                    config=types.GenerateContentConfig(system_instruction=PROMPT_EKSPERTA_PRIVATE, temperature=0.6)
                )
                
                embed = discord.Embed(title="🤖 ASYSTENT AI × MAKS REPS", description=response.text, color=0x5865F2)
                await message.reply(embed=embed)
            except Exception as e:
                print(f"❌ [BŁĄD AI PRIVATE] {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(PrivateChatCog(bot))
