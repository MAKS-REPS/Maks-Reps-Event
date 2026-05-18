import discord
from discord import app_commands
from discord.ext import commands

# 🎨 Dane do błyskawicznego ładowania w menu (Zero opóźnień)
BATCH_DATA = {
    "jordans": {
        "title": "👑 TOP BATCHE: KOLEKCJA JORDAN",
        "color": 0xff5733,
        "text": "• **Jordan 4:** `GX Batch` — Król dla Black Cat, Military Black, Pine Green. Idealny shape.\n"
                "• **Jordan 1:** `LJR Batch` — Najlepsza skóra. Dla modeli Travis Scott wybierz `PK 4.0`.\n"
                "• **Jordan 3:** `OG Batch` — Poprawiony elephant print.\n"
                "• **Jordan 11:** `LJR Batch` — Perfekcyjna lakierowana skóra."
    },
    "yeezy_dunk": {
        "title": "👟 SNEAKERS: YEEZY & NIKE DUNK",
        "color": 0x2ecc71,
        "text": "• **Nike Dunk Low:** `M Batch` — Konstrukcja 1:1, idealny kształt toeboxa.\n"
                "• **Yeezy 350 / 700:** `LW Batch` — Prawdziwy system Boost, ultra wygodne.\n"
                "• **Yeezy Slides / Foam:** `LW Batch` — Miękkie tworzywo, brak ostrych krawędzi.\n"
                "• **Air Force 1:** `XP Batch` — Najlepsza budżetówka, solidna skóra."
    },
    "designer": {
        "title": "💸 PREMIUM: BALENCIAGA & LUXURY",
        "color": 0xf1c40f,
        "text": "• **Balenciaga Track:** `OK Batch` — Wszystkie LEDy i siatki działają.\n"
                "• **Balenciaga Runner:** `VG Batch` — Świetny efekt postarzenia materiału.\n"
                "• **Louis Vuitton Trainer:** `Foshan Batch` (lub od Villian / Pone).\n"
                "• **Mihara Yasuhiro:** `W1 Batch` — Świetna jakość i masywna podeszwa."
    },
    "running": {
        "title": "🏃 STREETWEAR: ASICS & NEW BALANCE",
        "color": 0x3498db,
        "text": "• **ASICS (Kayano 14 / GEL-NYC):** `ZC Batch` — Najwygodniejsza podeszwa na co dzień.\n"
                "• **New Balance (2002R / 1906 / 550):** `ZC Batch` — Zamsz najwyższej klasy."
    }
}

class HubDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Kolekcja Jordan", description="J1, J3, J4, J11", emoji="👑", value="jordans"),
            discord.SelectOption(label="Yeezy & Dunki", description="Klasyki i wygoda", emoji="👟", value="yeezy_dunk"),
            discord.SelectOption(label="Balenciaga & Luxury", description="Marki luksusowe, LV, Mihara", emoji="💸", value="designer"),
            discord.SelectOption(label="Asics & New Balance", description="Wygodne sneakery", emoji="🏃", value="running"),
        ]
        super().__init__(placeholder="🔥 Wybierz markę/kategorię...", min_values=1, max_values=1, custom_id="hub_dropdown_prod")

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        data = BATCH_DATA[selection]
        
        embed = discord.Embed(title=data["title"], description=data["text"], color=data["color"])
        embed.set_footer(text="Maks Reps Hub • Wybierz inną kategorię w menu poniżej")
        
        await interaction.response.edit_message(embed=embed)

class HubView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(HubDropdown())

    @discord.ui.button(label="📦 Jak bezpiecznie deklarować?", style=discord.ButtonStyle.success, custom_id="hub_btn_declare_prod", row=1)
    async def btn_declare(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="📦 PORADNIK BEZPIECZNEJ DEKLARACJI",
            description="Aby Twoja paczka przeszła bezpiecznie przez urząd celny:\n\n"
                        "1. **Linie Tax Free (Bezclowe):** Zawsze deklaruj przedział między **$16 a $21** (np. `18.34`, `19.52`). Używaj końcówek po przecinku!\n"
                        "2. **Waga paczki:** Staraj się nie przekraczać **10kg** w jednej wysyłce.\n"
                        "3. **Zabezpieczenia:** Zawsze dokupuj *Stretch Film* oraz *Corner Protection*.",
            color=0x2ecc71
        )
        await interaction.response.send_message(embed=embed, ephemeral=False)

    @discord.ui.button(label="🛡️ Statusy Paczek & Cło", style=discord.ButtonStyle.danger, custom_id="hub_btn_customs_prod", row=1)
    async def btn_customs(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🛡️ STATUSY I UBEZPIECZENIE PACZKI",
            description="• **Customs Clearance / Inbound into Customs:** Paczka jest sprawdzana. Przy liniach *Tax Free* to standardowa procedura – bez paniki.\n"
                        "• **Zatrzymanie paczki?** Nigdy nie wysyłaj podrobionych dokumentów ani screenów bez konsultacji z administracją serwera!\n"
                        "• **Ubezpieczenie (Insurance):** Zawsze zaznaczaj opcję ubezpieczenia u agenta podczas wysyłki. Kosztuje grosze, a chroni w 100%.",
            color=0xe74c3c
        )
        await interaction.response.send_message(embed=embed, ephemeral=False)


class RepHubCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        # Rejestracja widoku dla trwałych przycisków po restarcie
        self.bot.add_view(HubView())

    # Komenda globalna Slash /setup_hub
    @app_commands.command(name="setup_hub", description="Generuje efektowne, interaktywne Centrum Wiedzy Maks Reps.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_hub(self, interaction: discord.Interaction):
        # Wysyłamy odpowiedź natychmiast, żeby uniknąć błędu "Aplikacja nie reaguje"
        embed = discord.Embed(
            title="⚡ MULTIMEDIALNE CENTRUM WIEDZY — MAKS REPS",
            description="Witamy w oficjalnym i najszybszym hubie informacyjnym serwera!\n\n"
                        "• **Użyj menu rozwijanego poniżej**, aby sprawdzić najlepsze batche.\n"
                        "• **Użyj przycisków**, aby wyświetlić poradniki wysyłkowe i celne.\n"
                        "• Potrzebujesz zaawansowanej pomocy? Użyj `/setup_ai_panel` aby otworzyć prywatny czat AI.",
            color=0x2f3136
        )
        await interaction.response.send_message(embed=embed, view=HubView())

async def setup(bot: commands.Bot):
    await bot.add_cog(RepHubCog(bot))
