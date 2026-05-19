
import discord
from discord import app_commands
from discord.ext import commands
from google import genai
from google.genai import types
import os
import asyncio

PROMPT_PRIVATE = """
Jesteś osobistym, prywatnym doradcą AI na serwerze Maks Reps. Odpowiadasz błyskawicznie, konkretnie i zwięźle. Używaj emotek.
Jeśli użytkownik prześle zdjęcie (butów lub odzieży), zrób szybkie QC: oceń kształt, szwy, jakość materiałów, nadruki, hafty i ogólne wykonanie, dając ocenę 1-10 oraz werdykt GL (Green Light) lub RL (Red Light).

TWOJA BAZA WIEDZY O BATCHACH (BUTY - STARA WERSJA):
- Nike Dunk -> M batch
- Jordan 4 -> GX batch (Black Cat, Military, Pine Green itp.)
- Jordan 1 -> LJR batch (do Travisów PK 4.0 / FK batch)
- Yeezy 350 / 700 -> LW batch
- New Balance / ASICS -> ZC batch
- Balenciaga Track -> OK batch
- Moncler -> Jieyi / TA

TWOJA BAZA WIEDZY O BATCHACH (UBRANIA - NOWA WERSJA):
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
        ai_channels = [c for c in guild.channels if "chat-" in c.name]
        
        embed = discord.Embed(
            title="🛠️ PANEL KONTROLNY MODERACJI AI",
            description="Tutaj wyświetlają się wszystkie aktywne, prywatne rozmowy użytkowników z botem. Lista aktualizuje się automatycznie.",
            color=0x2f3136
        )
        
        if ai_channels:
            links_text = ""
            for chan in ai_channels:
                # Ignorujemy główny kanał do tworzenia pokoi w panelu moderacji
                if chan.name == "chat-ai":
                    continue
                user_name = chan.name.replace("🧠-chat-", "").replace("chat-", "")
                links_text += f"• Pokój użytkownika: **{user_name}** -> <#{chan.id}>\n"
            embed.add_field(name=f"🟢 Aktywne czaty ({max(0, len(ai_channels)-1)}):", value=links_text, inline=False)
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
            description="### 👟 OBUWIE (STARA WERSJA):\n"
                        "• **Nike Dunk:** M batch\n"
                        "• **Jordan 4:** GX batch (Black Cat, Military, Pine Green itp.)\n"
                        "• **Jordan 1:** LJR batch (do Travisów PK 4.0 / FK batch)\n"
                        "• **Yeezy 350 / 700:** LW batch\n"
                        "• **New Balance / ASICS:** ZC batch\n"
                        "• **Balenciaga Track:** OK batch\n"
                        "• **Moncler:** Jieyi / TA\n\n"
                        "### 👕 ODZIEŻ (NOWA WERSJA):\n"
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
        # 👑 Blokada - tylko Owner serwera może zamknąć chat
        if interaction.user.id != interaction.guild.owner_id:
            return await interaction.response.send_message(
                "❌ Tylko **Owner serwera** ma uprawnienia do zamknięcia tego pokoju AI!", 
                ephemeral=True
            )

        await interaction.response.defer()
        
        channel = interaction.channel
        guild = interaction.guild
        user_name = channel.name.replace("🧠-chat-", "").replace("chat-", "")
        
        # Tworzenie transkryptu rozmowy przed usunięciem
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

        # 🎬 Mini animacja paska ładowania przed usunięciem kanału
        anim_embed = discord.Embed(
            title="🔒 ZAMYKANIE POKOJU AI",
            description="⚙️ Zapisywanie historii czatu...\n`[⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜]` 0%",
            color=discord.Color.red()
        )
        anim_msg = await interaction.followup.send(embed=anim_embed)
        
        frames = [
            ("⚙️ Generowanie archiwum i logów...\n`[🟩🟩🟩⬜⬜⬜⬜⬜⬜⬜]` 30%", 0.6),
            ("⚙️ Aktualizacja panelu administratora...\n`[🟩🟩🟩🟩🟩🟩🟩⬜⬜⬜]` 70%", 0.6),
            ("⚠️ Pokój zostanie usunięty za **3**...\n`[🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩]` 100%", 1.0),
            ("⚠️ Pokój zostanie usunięty za **2**...\n`[🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩]` 100%", 1.0),
            ("⚠️ Pokój zostanie usunięty za **1**...\n`[🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩]` 100%", 1.0)
        ]
        
        for text, delay in frames:
            await asyncio.sleep(delay)
            anim_embed.description = text
            await anim_msg.edit(embed=anim_embed)

        await asyncio.sleep(0.2)
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

        existing = [c for c in guild.channels if "chat-" in c.name and clean_nick in c.name]
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
            description=f"Siemanko <@{user.id}>! Napisz po prostu swoją wiadomość tekstową poniżej lub **wyślij zdjęcie**, a asystent od razu Ci odpowie!\n\n"
                        f"• Kiedy skończysz rozmowę, Owner serwera będzie mógł kliknąć czerwony przycisk poniżej, aby zamknąć ten kanał.",
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
            description="Potrzebujesz ekspresowej pomocy eksperta modowego? Chcesz sprawdzić jakość swoich replik ze zdjęć od agenta?\n\n"
                        "### 🪐 Co potrafi nasz system AI?\n"
                        "• **Natychmiastowe QC:** Wyślij zdjęcie, a bot sprawdzi szwy, kształt i wystawi werdykt **GL/RL**.\n"
                        "• **Dobór Batchy:** Pomoże dobrać najlepszą fabrykę pod wybrane buty lub ubrania.\n"
                        "• **Wsparcie Techniczne:** Odpowie na pytania o cło, bezpieczne linie wysyłkowe i deklaracje.\n\n"
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
        
        os.environ["AI_ADMIN_CHANNEL_ID"] = str(interaction.channel.id)
        os.environ["AI_ADMIN_MSG_ID"] = str(msg.id)
        
        await refresh_admin_panel(interaction.guild)
        await interaction.followup.send("✅ Panel został pomyślnie utworzony!", ephemeral=True)

    # 🔥 AUTOMATYCZNE ODPOWIADANIE NA ZWYKŁY TEKST NA KANAŁACH PRYWATNYCH CHATÓW
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        channel_name = str(getattr(message.channel, 'name', '')).lower()
        
        # Blokujemy reagowanie na głównym kanale "chat-ai", bot odpowiada tylko w pokojach prywatnych użytkowników
        if "chat-" in channel_name and channel_name != "chat-ai":
            if not self.ai_client:
                return

            async with message.channel.typing():
                try:
                    contents_payload = []

                    if message.attachments:
                        for attachment in message.attachments:
                            if attachment.content_type and attachment.content_type.startswith("image/"):
                                img_bytes = await attachment.read()
                                contents_payload.append(
                                    types.Part.from_bytes(data=img_bytes, mime_type=attachment.content_type)
                                )
                    
                    contents_payload.append(types.Part.from_text(text=message.content))

                    response = self.ai_client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=contents_payload,
                        config=types.GenerateContentConfig(system_instruction=PROMPT_PRIVATE, temperature=0.3)
                    )

                    title_text = "📸 WYNIK SZYBKIEGO QC" if message.attachments else "🤖 ODPOWIEDŹ AI"
                    embed = discord.Embed(title=title_text, description=response.text, color=0x5865F2)
                    await message.reply(embed=embed)

                except Exception as e:
                    print(f"❌ [BŁĄD PRYWATNEGO CZATU] {e}")
                    await message.channel.send("⚠️ Coś poszło nie tak podczas generowania odpowiedzi przez AI.")

async def setup(bot: commands.Bot):
    await bot.add_cog(PrivateChatCog(bot))
