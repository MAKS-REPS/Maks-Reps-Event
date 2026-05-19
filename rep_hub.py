import discord
from discord import app_commands
from discord.ext import commands

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
    },
    # 🔥 NOWOŚĆ: Pełna lista odzieży w Hubie
    "clothes": {
        "title": "👕 STREETWEAR & APPAREL: NAJLEPSZE BATCHE",
        "color": 0x9b59b6,
        "text": "• **Denim Tears:** `Angelking` — Najlepsze puffy printy.\n"
                "• **Syna World / Trapstar / Corteiz:** `GOAT` — Niekwestionowany król tych marek.\n"
                "• **Sp5der:** `PIKA` — Świetna jakość dresów i nadruków.\n"
                "• **Ami:** `RepsBrothers` — Perfekcyjne hafty i serca.\n"
                "• **Essentials (FOG) / Chrome Hearts:** `Tophot`\n"
                "• **Burberry:** `Thethunder`\n"
                "• **Stone Island:** `TopStoney` — Klasyk, materiały reagujące na ciepło/guziki 1:1.\n"
                "• **Stussy:** `ZS Factory`\n"
                "• **Polo Ralph Lauren:** `Newdp`\n"
                "• **Nike Tech Fleece:** `Husky` — Najlepszy krój i gruby materiał.\n"
                "• **Supreme:** `Subway Hooligan` — Świetne bogo."
    }
}

class HubDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Kolekcja Jordan", description="J1, J3, J4, J11", emoji="👑", value="jordans"),
            discord.SelectOption(label="Yeezy & Dunki", description="Klasyki i wygoda", emoji="👟", value="yeezy_dunk"),
            discord.SelectOption(label="Balenciaga & Luxury", description="Marki luksusowe, LV, Mihara", emoji="💸", value="designer"),
            discord.SelectOption(label="Asics & New Balance", description="Wygodne sneakery", emoji="🏃", value="running"),
            discord.SelectOption(label="Odzież & Streetwear", description="Dresy, T-shirty, Kurtki", emoji="👕", value="clothes"),
        ]
        super().__init__(placeholder="🔥 Wybierz markę/kategorię...", min_values=1, max_values=1, custom_id="hub_dropdown_prod", options=options)

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
                        "1. **Linie Tax Free (Bezclowe):** Deklaruj wartość paczki zgodnie z aktualnymi widełkami podanymi przez wybranego agenta. **Zawsze używaj losowych końcówek po przecinku** (np. zamiast równej kwoty wpisz końcówkę `.34` lub `.52`), co wygląda naturalnie dla systemu celnego.\n"
                        "2. **Waga paczki:** Staraj się nie przekraczać wagi **10kg** w jednej wysyłce. Jeśli masz większe zakupy, bezpieczniej jest podzielić je na dwie osobne paczki.\n"
                        "3. **Zabezpieczenia paczki:** W opcjach pakowania zawsze zaznaczaj **Stretch Film** (foliowanie) oraz **Corner Protection** (ochraniacze na rogi kartonu). Utrudnia to otwarcie paczki i chroni przed uszkodzeniem.",
            color=0x2ecc71
        )
        await interaction.response.send_message(embed=embed, ephemeral=False)

    @discord.ui.button(label="🛡️ Statusy Paczek & Cło", style=discord.ButtonStyle.danger, custom_id="hub_btn_customs_prod", row=1)
    async def btn_customs(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🛡️ STATUSY I UBEZPIECZENIE PACZKI",
            description="• **Customs Clearance / Inbound into Customs:** Paczka przechodzi standardową weryfikację. Przy liniach *Tax Free* to w pełni rutynowa procedura.\n"
                        "• **Weryfikacja dokumentów?** Nigdy nie generuj ani nie wysyłaj pism na własną rękę bez uprzedniej konsultacji z administracją serwera!\n"
                        "• **Ubezpieczenie (Insurance):** Zawsze zaznaczaj opcję pełnego ubezpieczenia przesyłki u agenta podczas wysyłki dla pełnego bezpieczeństwa.",
            color=0xe74c3c
        )
        await interaction.response.send_message(embed=embed, ephemeral=False)


class RepHubCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        self.bot.add_view(HubView())

    @app_commands.command(name="setup_hub", description="Generuje efektowne, interaktywne Centrum Wiedzy Maks Reps.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_hub(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)

        try:
            embed = discord.Embed(
                title="⚡ MULTIMEDIALNE CENTRUM WIEDZY — MAKS REPS",
                description="Witamy w oficjalnym i najszybszym hubie informacyjnym serwera!\n\n"
                            "• **Użyj menu rozwijanego poniżej**, aby sprawdzić najlepsze batche.\n"
                            "• **Użyj przycisków**, aby wyświetlić poradniki wysyłkowe i celne.\n"
                            "• Potrzebujesz zaawansowanej pomocy? Użyj `/setup_ai_panel` aby otworzyć prywatny czat AI.",
                color=0x2f3136
            )
            await interaction.followup.send(embed=embed, view=HubView())
        except Exception as e:
            print(f"❌ [BŁĄD HUB SETUP] {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(RepHubCog(bot))
