import discord
from discord import app_commands
from discord.ext import commands
from google import genai
from google.genai import types
import os
import io

PROMPT_PRIVATE = """
Jesteś osobistym, prywatnym doradcą AI na serwerze Maks Reps. Odpowiadasz błyskawicznie, konkretnie i zwięźle. Używaj emotek.
Jeśli użytkownik prześle zdjęcie (butów lub odzieży), zrób szybkie QC: oceń kształt, szwy, jakość materiałów, nadruki, hafty i ogólne wykonanie, dając ocenę 1-10 oraz werdykt GL (Green Light) lub RL (Red Light).

TWOJA BAZA WIEDZY O BATCHACH (BUTY):
- Nike Dunk -> M Batch
- Jordan 4 -> GX Batch (Black Cat, Military, Pine Green)
- Jordan 1 -> LJR (PK 4.0 dla modeli Travis Scott)
- Yeezy -> LW Batch
- New Balance / ASICS -> ZC Batch
- Numeris -> W1 | Balenciaga Track -> OK | LV -> Foshan

TWOJA BAZA WIEDZY O BATCHACH (UBRANIA):
- Denim Tears -> Angelking
- Syna World / Trapstar / Corteiz -> GOAT
- Sp5der -> PIKA
- Ami -> RepsBrothers
- Essentials (FOG) / Chrome Hearts -> Tophot
- Burberry -> Thethunder
- Stone Island -> TopStoney
- Stussy -> ZS Factory
- Polo Ralph Lauren -> Newdp
- Nike Tech Fleece -> Husky
- Supreme -> Subway Hooligan

ZASADY: Skupiasz się wyłącznie na jakości, dopasowaniu (fitowaniu) i doborze najlepszych fabryk. Nigdy nie wspominaj o konkretnych cenach, kosztach, walutach ani kwotach zniżek.

REFLINK I KUPONY:
- Rejestracja: https://ikako.vip/r/maksr3ps
- Kody: Maks.R3ps | Maks20
"""

if not os.path.exists("ai_transcripts"):
    os.makedirs("ai_transcripts")


async def refresh_admin_panel(guild: discord.Guild):
    panel_channel_id = os.getenv("AI_ADMIN_CHANNEL_ID")
    panel_msg_id = os.getenv("AI_ADMIN_MSG_ID")
    
    if not panel_channel_id or not panel_msg_id:
        return 
        
    try:
        channel = guild.get_channel(int(panel_channel_id))
        if not channel:
            return
            
        msg = await channel.fetch_message(int(panel_msg_id))
        ai_channels = [c for c in guild.channels if c.name.startswith("🧠-chat-")]
        
        embed = discord.Embed(
            title="🛠️ PANEL KONTROLNY MODERACJI AI",
            description="Tutaj wyświetlają się wszystkie aktywne, prywatne rozmowy użytkowników z botem. Lista aktualizuje się automatycznie.",
            color=0x2f3136
        )
        
        if ai_channels:
            links_text = ""
            for chan in ai_channels:
                user_name = chan.name.replace("🧠-chat-", "")
                links_text += f"• Pokój użytkownika: **{user_name}** -> <#{chan.id}>\n"
            embed.add_field(name=f"🟢 Aktywne czaty ({len(ai_channels)}):", value=links_text, inline=False)
        else:
            embed.add_field(name="🔴 Aktywne czaty (0):", value="W tej chwili nikt nie prowadzi rozmowy z ekspertem AI.", inline=False)
            
        embed.set_footer(text="Maks Reps System • Live Updates")
        await msg.edit(embed=embed)
        
    except Exception as e:
        print(f"❌ [BŁĄD AKTUALIZACJI PANELU ADMINA] {e}")


class TicketAddonsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="👟 Lista Best Batchy (Buty i Ubrania)", style=discord.ButtonStyle.secondary, custom_id="faq_batche")
    async def faq_batche(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="👟 Oficjalna Lista Best Batchów",
            description="### 👟 OBUWIE:\n"
                        "• **Nike Dunk:** M Batch | **Jordan 4:** GX Batch\n"
                        "• **Jordan 1:** LJR / PK 4.0 | **Yeezy:** LW Batch\n"
                        "• **ASICS / NB:** ZC Batch | **Balenciaga Track:** OK\n\n"
                        "### 👕 ODZIEŻ:\n"
                        "• **Denim Tears:** Angelking\n"
                        "• **Syna / Trapstar / Corteiz:** GOAT\n"
                        "• **Sp5der:** PIKA | **Ami:** RepsBrothers\n"
                        "• **Essentials / Chrome Hearts:** Tophot\n"
                        "• **Burberry:** Thethunder | **Stone Island:** TopStoney\n"
                        "• **Stussy:** ZS Factory | **Polo RL:** Newdp\n"
                        "• **Nike Tech:** Husky | **Supreme:** Subway Hooligan",
            color=0x9b59b6
        )
        await interaction.response.send_message(embed=embed, ephemeral=False)

    @discord.ui.button(label="🎁 Link do Agenta & Kody", style=discord.ButtonStyle.success, custom_id="faq_kupony")
    async def faq_kupony(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🎁 Rejestracja u Agenta i Bonusy",
            description="🎁 [Zarejestruj się klikając tutaj](https://ikako.vip/r/maksr3ps)\n\n"
                        "🔥 **Kody zniżkowe do użycia przy wysyłce paczki:**\n"
                        "• Pierwszy kod: `Maks.R3ps`\n"
                        "• Drugi kod: `Maks20`",
            color=0x2ecc71
        )
        await interaction.response.send_message(embed=embed, ephemeral=False)


class ChatCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Zamknij i usuń chat", style=discord.ButtonStyle.danger, custom_id="close_ai_chat_prod")
    async def close_chat(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        channel = interaction.channel
        guild = interaction.guild
        user_name = channel.name.replace("🧠-chat-", "")
        
        transcript_text = f"=== ARCHIWUM ROZMOWY AI: {user_name.upper()} ===\n\n"
        async for msg in channel.history(limit=150, oldest_first=True):
            if msg.embeds and "Twój Prywatny Ekspert AI" in (msg.embeds[0].title or ""):
                continue
            
            author = "BOT (AI)" if msg.author.bot else f"UŻYTKOWNIK (@{msg.author.name})"
            content = msg.embeds[0].description if (msg.author.bot and msg.embeds) else msg.content
            transcript_text += f"[{msg.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {author}: {content}\n\n"
            
        transcript_text += "=== KONIEC ZAPISU ==="
        
        file_path = f"ai_transcripts/chat-{user_name}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(transcript_text)

        await channel.delete()
        await refresh_admin_panel(guild)


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

        category = interaction.channel.category if hasattr(interaction.channel, 'category') else None
        new_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites, category=category)
        
        welcome_embed = discord.Embed(
            title="🧠 Twój Prywatny Ekspert AI",
            description=f"Siemanko <@{user.id}>! Napisz poniżej swoje pytanie lub **użyj komendy `/zapytaj_ai`** aby uzyskać odpowiedź lub zrobić **QC zdjęcia**!\n\n"
                        f"• Kiedy skończiesz rozmowę, kliknij czerwony przycisk poniżej, aby zamknąć ten kanał.",
            color=0x5865F2
        )
        
        await new_channel.send(embed=welcome_embed, view=ChatCloseView())
        await new_channel.send("⚡ **Szybkie informacje (widoczne dla wszystkich):**", view=TicketAddonsView())
        await interaction.followup.send(f"✅ Twój pokój AI: <#{new_channel.id}>", ephemeral=True)
        
        await refresh_admin_panel(guild)


class PrivateChatCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        api_key = os.getenv("GEMINI_API_KEY")
        self.ai_client = genai.Client(api_key=api_key) if api_key else None

    async def cog_load(self):
        self.bot.add_view(ChatCreateView())
        self.bot.add_view(ChatCloseView())
        self.bot.add_view(TicketAddonsView())

    @app_commands.command(name="setup_ai_panel", description="Generuje panel biletów prywatnego AI.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_ai_panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🧠 PRYWATNY SYSTEM WSPARCIA AI × MAKS REPS",
            description="Potrzebujesz ekspresowej pomocy eksperta modowego? Chcesz sprawdzić jakość swoich przedmiotów ze zdjęć od agenta?\n\n"
                        "### 🪐 Co potrafi nasz system AI?\n"
                        "• **Natychmiastowe QC:** Wyślij zdjęcie, a bot oceni detale, kształt i wystawi werdykt **GL/RL**.\n"
                        "• **Dobór Batchy:** Pomoże dobrać najlepszą fabrykę pod konkretne modele butów lub ubrań.\n"
                        "• **Wsparcie Techniczne:** Odpowie na pytania o statusy paczek, bezpieczne linie wysyłkowe i deklaracje.\n\n"
                        "📌 *Kliknij przycisk poniżej, aby utworzyć swój w pełni prywatny, zabezpieczony kanał 1-na-1.*",
            color=0x5865F2
        )
        embed.set_footer(text="Maks Reps • Inteligentny Asystent 24/7")
        await interaction.response.send_message(embed=embed, view=ChatCreateView())

    @app_commands.command(name="setup_admin_panel", description="Tylko dla Ownera: Tworzy automatyczny panel podglądu aktywnych chatów AI.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_admin_panel(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        embed = discord.Embed(
            title="🛠️ PANEL KONTROLNY MODERACJI AI",
            description="Inicjalizacja panelu... Za chwilę pojawią się tu aktywne pokoje.",
            color=0x2f3136
        )
        
        msg = await interaction.channel.send(embed=embed)
        
        print(f"\n🚀 [KONFIGURACJA PANELU] Przypisz te wartości w ustawieniach Railway:\n"
              f"AI_ADMIN_CHANNEL_ID = {interaction.channel.id}\n"
              f"AI_ADMIN_MSG_ID = {msg.id}\n")
              
        os.environ["AI_ADMIN_CHANNEL_ID"] = str(interaction.channel.id)
        os.environ["AI_ADMIN_MSG_ID"] = str(msg.id)
        
        await refresh_admin_panel(interaction.guild)
        await interaction.followup.send("✅ Panel został pomyślnie utworzony! Od teraz będzie się sam aktualizował.", ephemeral=True)

    @app_commands.command(name="zapytaj_ai", description="Zadaj pytanie asystentowi lub prześlij zdjęcie do szybkiego QC.")
    async def zapytaj_ai(self, interaction: discord.Interaction, pytanie: str, zdjecie: discord.Attachment = None):
        ALLOWED_CHANNEL_ID = 1506026307329196242
        
        if interaction.channel.id != ALLOWED_CHANNEL_ID and not interaction.channel.name.startswith("🧠-chat-"):
            return await interaction.response.send_message(
                f"❌ Tej komendy możesz używać wyłącznie na dedykowanym kanale publicznym <#{ALLOWED_CHANNEL_ID}> lub w Twoim prywatnym pokoju AI!", 
                ephemeral=True
            )

        if not self.ai_client:
            return await interaction.response.send_message("❌ Błąd konfiguracji API.", ephemeral=True)

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
            
            error_str = str(e).lower()
            if "503" in error_str or "high demand" in error_str or "unavailable" in error_str:
                embed_error = discord.Embed(
                    title="⏳ Serwery AI są chwilowo zajęte",
                    description="W tej chwili serwery Google Gemini przetwarzają ogromną liczbę żądań na świecie.\n\n"
                                "🔥 **Co zrobić?**\n"
                                "Nie martw się, to zazwyczaj chwilowe! Odczekaj około **15-30 sekund** i użyj komendy `/zapytaj_ai` ponownie.",
                    color=0xe67e22
                )
                await interaction.followup.send(embed=embed_error)
            else:
                await interaction.followup.send("⚠️ Coś poszło nie tak podczas generowania odpowiedzi przez AI. Spróbuj ponownie za chwilę.")

async def setup(bot: commands.Bot):
    await bot.add_cog(PrivateChatCog(bot))
