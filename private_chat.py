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

TWOJA BAZA WIEDZY O BATCHACH (BUTY - STARA, NAJLEPSZA WERSJA):
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

# --- KONFIGURACJA SYSTEMU TICKETÓW ---
ID_KATEGORII_TICKETOW = 1486842150661656767
REQUIRED_ROLE_ID = 1457769309735485450
MAKS_BLUE = 0x3498db

if not os.path.exists("ai_transcripts"):
    os.makedirs("ai_transcripts")


class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Zamknij ticket", style=discord.ButtonStyle.danger, custom_id="persistent_close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 👑 Sprawdzenie Ownera serwera
        if interaction.user.id != interaction.guild.owner_id:
            return await interaction.response.send_message(
                "❌ Tylko **Owner serwera** ma uprawnienia do zamknięcia tego ticketu!", 
                ephemeral=True
            )
        
        await interaction.response.defer()
        
        # 🎬 Mini animacja zamykania kanału
        anim_embed = discord.Embed(
            title="🔒 PROCEDURA ZAMYKANIA TICKETU",
            description="⚙️ Inicjalizacja procesu kasowania pokoju...\n`[⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜]` 0%",
            color=discord.Color.red()
        )
        
        msg = await interaction.followup.send(embed=anim_embed)
        
        frames = [
            ("⚙️ Generowanie archiwum rozmowy...\n`[🟩🟩🟩⬜⬜⬜⬜⬜⬜⬜]` 30%", 0.6),
            ("⚙️ Czyszczenie uprawnień i ról...\n`[🟩🟩🟩🟩🟩🟩🟩⬜⬜⬜]` 70%", 0.6),
            ("⚠️ Kanał zostanie bezpowrotnie usunięty za **3**...\n`[🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩]` 100%", 1.0),
            ("⚠️ Kanał zostanie bezpowrotnie usunięty za **2**...\n`[🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩]` 100%", 1.0),
            ("⚠️ Kanał zostanie bezpowrotnie usunięty za **1**...\n`[🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩]` 100%", 1.0)
        ]
        
        for text, delay in frames:
            await asyncio.sleep(delay)
            anim_embed.description = text
            await msg.edit(embed=anim_embed)
            
        await asyncio.sleep(0.2)
        await interaction.channel.delete()


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


class TicketMenu(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="POMOC", description="Ogólna pomoc i pytania", emoji="❓"),
            discord.SelectOption(label="POMOC Z ZAMÓWIENIEM", description="Kliknij, jeśli potrzebujesz pomocy z zamówieniem", emoji="🛒"),
            discord.SelectOption(label="PROBLEM Z SHIPPINGIEM", description="Kliknij, jeśli masz problem z shippingiem", emoji="🚛"),
            discord.SelectOption(label="DOSTĘP", description="Kliknij, aby uzyskać dostęp", emoji="🔑"),
            discord.SelectOption(label="WSPÓŁPRACA", description="Chcesz zostać naszym promotorem? Kliknij tutaj!", emoji="🤝"),
        ]
        super().__init__(
            placeholder="❌ Nie wybrano żadnej z kategorii", 
            min_values=1, 
            max_values=1, 
            options=options, 
            custom_id="persistent_ticket_select"
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = guild.get_channel(ID_KATEGORII_TICKETOW)
        admin_role = guild.get_role(REQUIRED_ROLE_ID)
        
        if not category or not admin_role:
            return await interaction.response.send_message("❌ Błąd konfiguracji serwera (brak kategorii lub roli).", ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            admin_role: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True)
        }
        
        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name.lower().replace(' ', '-')}", 
            category=category, 
            overwrites=overwrites
        )
        
        embed = discord.Embed(
            title="🎫 MAKS REPS × TICKET", 
            description=f"Witaj {interaction.user.mention}!\nWybrałeś kategorię: **{self.values[0]}**.\nZaraz ktoś z administracji Ci pomoże.\n\n🤖 Na tym kanale możesz rozmawiać bezpośrednio pisząc zwykłe wiadomości tekstowe, a AI Ci odpowie!", 
            color=MAKS_BLUE
        )
        
        await channel.send(content=f"{interaction.user.mention} | {admin_role.mention}", embed=embed, view=TicketCloseView())
        await channel.send("⚡ **Szybkie informacje (widoczne dla wszystkich):**", view=TicketAddonsView())
        await interaction.response.send_message(f"✅ Otwarto ticket: {channel.mention}", ephemeral=True)


class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketMenu())


class PrivateChatCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        api_key = os.getenv("GEMINI_API_KEY")
        self.ai_client = genai.Client(api_key=api_key) if api_key else None

    async def cog_load(self):
        self.bot.add_view(TicketView())
        self.bot.add_view(TicketCloseView())
        self.bot.add_view(TicketAddonsView())

    @app_commands.command(name="setup_ai_panel", description="Generuje panel biletów prywatnego AI.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_ai_panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🧠 PRYWATNY SYSTEM WSPARCIA AI × MAKS REPS",
            description="Potrzebujesz ekspresowej pomocy eksperta modowego? Chcesz sprawdzić jakość swoich przedmiotów ze zdjęć od agenta?\n\n"
                        "📌 *Kliknij wybór poniżej, aby utworzyć kanał wsparcia.*",
            color=MAKS_BLUE
        )
        await interaction.response.send_message(embed=embed, view=TicketView())

    # 🔥 REAKCJA NA ZWYKŁY CHAT TEKSTOWY W PRYWATNYCH KANAŁACH
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignoruj wiadomości od samego bota
        if message.author.bot:
            return

        channel_name = message.channel.name.lower() if message.channel and hasattr(message.channel, 'name') else ""
        
        # Sprawdzamy czy to bilet lub dedykowany chat prywatny
        if "chat-" in channel_name or "ticket-" in channel_name:
            if not self.ai_client:
                return

            # Wywołujemy efekt pisania ("bot is typing..."), aby czat wyglądał naturalnie
            async with message.channel.typing():
                try:
                    contents_payload = []

                    # Obsługa załączników (zdjęć do QC)
                    if message.attachments:
                        for attachment in message.attachments:
                            if attachment.content_type and attachment.content_type.startswith("image/"):
                                img_bytes = await attachment.read()
                                contents_payload.append(
                                    types.Part.from_bytes(data=img_bytes, mime_type=attachment.content_type)
                                )
                    
                    contents_payload.append(types.Part.from_text(text=message.content))

                    # Generowanie odpowiedzi przez model Gemini
                    response = self.ai_client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=contents_payload,
                        config=types.GenerateContentConfig(system_instruction=PROMPT_PRIVATE, temperature=0.3)
                    )

                    title_text = "📸 WYNIK SZYBKIEGO QC" if message.attachments else "🤖 ODPOWIEDŹ AI"
                    embed = discord.Embed(title=title_text, description=response.text, color=MAKS_BLUE)
                    
                    # Odpowiedź bezpośrednio oznaczając (reply) użytkownika
                    await message.reply(embed=embed)

                except Exception as e:
                    print(f"❌ [BŁĄD CZATU AI] {e}")
                    await message.channel.send("⚠️ Coś poszło nie tak podczas generowania odpowiedzi przez AI. Spróbuj ponownie za chwilę.")


async def setup(bot: commands.Bot):
    await bot.add_cog(PrivateChatCog(bot))
