import discord
from discord import app_commands
from discord.ext import commands
import os

# 🎨 Słownik z ultra-czystymi danymi (Błyskawiczne ładowanie)
BATCH_DATA = {
    "jordans": {
        "title": "👑 KROK PO KROKU: BATCHE NA JORDAN",
        "color": 0xff5733,
        "text": "• **Jordan 4:** `GX Batch` — Absolutny król dla Black Cat, Military Black, Pine Green. Idealny shape.\n"
                "• **Jordan 1:** `LJR Batch` — Najlepsza skóra i wysoka jakość. Dla Travisów wybierz `PK 4.0`.\n"
                "• **Jordan 3:** `OG Batch` — Poprawiony elephant print, najlepszy na rynku.\n"
                "• **Jordan 11:** `LJR Batch` — Perfekcyjna lakierowana skóra."
    },
    "yeezy_dunk": {
        "title": "👟 SNEAKERS: YEEZY & NIKE DUNK",
        "color": 0x2ecc71,
        "text": "• **Nike Dunk Low:** `M Batch` — Konstrukcja 1:1, idealny kształt toeboxa i stitching.\n"
                "• **Yeezy 350 / 700:** `LW Batch` — Prawdziwy system Boost, wygoda jak w oryginale.\n"
                "• **Yeezy Slides / Foam:** `LW Batch` — Miękkie tworzywo, brak ostrych krawędzi odlewów.\n"
                "• **Air Force 1:** `XP Batch` — Dobra budżetówka, solidna skóra."
    },
    "designer": {
        "title": "💸 PREMIUM: BALENCIAGA & LUXURY",
        "color": 0xf1c40f,
        "text": "• **Balenciaga Track:** `OK Batch` — Wszystkie LEDy i siatki działają idealnie.\n"
                "• **Balenciaga Runner:** `VG Batch` — Idealny efekt postarzenia materiału.\n"
                "• **Louis Vuitton Trainer:** `Foshan Batch` (lub od sprzedawców Villian / Pone).\n"
                "• **Mihara Yasuhiro:** `W1 Batch` — Świetna cena (ok. 180zł), masywna podeszwa."
    },
    "running": {
        "title": "🏃 STREETWEAR: ASICS & NEW BALANCE",
        "color": 0x3498db,
        "text": "• **ASICS (Kayano 14 / GEL-NYC):** `ZC Batch` — Najwygodniejsza podeszwa, cena ok. 130zł.\n"
                "• **New Balance (2002R / 1906 / 550):** `ZC Batch` — Świetne materiały, zamsz najwyższej klasy."
    }
}

# Menu rozwijane dla kategorii butów
class HubDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Kolekcja Jordan", description="J1, J3, J4, J11 (Wszystkie topowe batche)", emoji="👑", value="jordans"),
            discord.SelectOption(label="Yeezy & Dunki", description="Wygoda i klasyka (M, LW, XP Batche)", emoji="👟", value="yeezy_dunk"),
            discord.SelectOption(label="Balenciaga & Luxury", description="Marki premium, LV, Mihara", emoji="💸", value="designer"),
            discord.SelectOption(label="Asics & New Balance", description="Wygodne sneakery na co dzień", emoji="🏃", value="running"),
        ]
        super().__init__(placeholder="🔥 Wybierz markę/kategorię ubrań...", min_values=1, max_values=1, custom_id="hub_dropdown")

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        data = BATCH_DATA[selection]
        
        embed = discord.Embed(title=data["title"], description=data["text"], color=data["color"])
        embed.set_footer(text="Maks Reps Hub • Wybierz inną kategorię w menu poniżej")
        
        # Edycja wiadomości następuje w ułamku sekundy (0ms opóźnienia z AI)
        await interaction.response.edit_message(embed=embed)

# Przyciski pomocnicze na dole dashboardu
class HubView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(HubDropdown())

    @discord.ui.button(label="📦 Jak bezpiecznie deklarować?", style=discord.ButtonStyle.success, custom_id="hub_btn_declare", row=1)
    async def btn_declare(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="📦 PROFESJONALNY PORADNIK DEKLARACJI",
            description="Aby Twoja paczka przeszła bezpiecznie przez urząd celny:\n\n"
                        "1. **Linie Tax Free (Bezclowe):** Zawsze deklaruj między **$16 a $21** (np. `18.43`). Pamiętaj o końcówkach po przecinku!\n"
                        "2. **Waga paczki:** Staraj się nie przekraczać **10kg** w jednej wysyłce.\n"
                        "3. **Dodatki:** Zawsze dokupuj *Stretch Film* oraz *Corner Protection* — celnikom nie chce się otwierać mocno zafoliowanych paczek.",
            color=0x2ecc71
        )
        await interaction.response.send_message(embed=embed, ephemeral=False)

    @discord.ui.button(label="🛡️ Statusy Paczek & Cło", style=discord.ButtonStyle.danger, custom_id="hub_btn_customs", row=1)
    async def btn_customs(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🛡️ OCHRONA PRZED CŁEM & INTERPRETACJA STATUSÓW",
            description="• **Customs Clearance / Inbound into Customs:** Twoja paczka jest sprawdzana. Jeśli leczenia użyłeś linii *Tax Free*, nie masz się czego bać.\n"
                        "• **Co zrobić w przypadku zatrzymania?** Nigdy nie wysyłaj podrobionych screenów z banku bez konsultacji z Administracją serwera!\n"
                        "• **Ubezpieczenie (Insurance):** Zawsze dokupuj pełne ubezpieczenie paczki u agenta. Kosztuje grosze, a chroni w 100%.",
            color=0xe74c3c
        )
        await interaction.response.send_message(embed=embed, ephemeral=False)

    @discord.ui.button(label="🧠 Zapytaj AI o coś innego", style=discord.ButtonStyle.primary, custom_id="ai_chat_button_prod", row=1)
    async def btn_call_ai(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Przycisk automatycznie uruchamia genialną logikę tworzenia kanału prywatnego z private_chat.py!
        pass


class RepHubCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        self.bot.add_view(HubView())

    @app_commands.command(name="setup_hub", description="Generuje efektowne, interaktywne Centrum Wiedzy Maks Reps.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_hub(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="⚡ MULTIMEDIALNE CENTRUM WIEDZY — MAKS REPS",
            description="Witamy w najszybszym hubie informacyjnym na świecie! Co chcesz sprawdzić?\n\n"
                        "• **Użyj menu poniżej**, aby błyskawicznie sprawdzić Best Batche.\n"
                        "• **Użyj przycisków**, aby poznać tajniki bezpiecznej wysyłki paczek.\n"
                        "• Nie znalazłeś odpowiedzi? Kliknij niebieski przycisk, by wezwać **Sztuczną Inteligencję**.",
            color=0x2f3136
        )
        embed.set_image(url="https://ikako.vip/r/maksr3ps") # Opcjonalnie możesz tu wkleić bezpośredni link do ładnej grafiki baneru
        await interaction.response.send_message(embed=embed, view=HubView())

async def setup(bot: commands.Bot):
    await bot.add_cog(RepHubCog(bot))
