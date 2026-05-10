async def start_animation(self, interaction, bet_type):
    # Klatki animacji z "podświetleniem" strzałkami
    # Symulujemy przeskakiwanie światła po bębenku
    frames = [
        "**> 🟥 <** ⬛ 🟥 ⬛ 🟥",
        "🟥 **> ⬛ <** 🟥 ⬛ 🟥",
        "🟥 ⬛ **> 🟥 <** ⬛ 🟥",
        "🟥 ⬛ 🟥 **> ⬛ <** 🟥",
        "🟥 ⬛ 🟥 ⬛ **> 🟥 <**",
        "**> ⬛ <** 🟥 ⬛ 🟥 ⬛",
        "⬛ **> 🟩 <** ⬛ 🟥 ⬛" # Zielony mignie tylko raz w animacji dla emocji
    ]
    
    for frame in frames:
        await interaction.edit_original_response(
            content=f"🎰 **TRWA LOSOWANIE...**\n\n{frame}\n\n*Powodzenia!*", 
            view=None
        )
        await asyncio.sleep(0.4) # Szybkość "migania"

    # --- LOGIKA LOSOWANIA (ZIELONY 0.5%) ---
    # 1-5: Zielony (0.5%), 6-503: Czerwony (49.75%), 504-1000: Czarny (49.75%)
    rand = random.randint(1, 1000)
    
    if rand <= 5:
        result_color = "zielony"
        result_emoji = "🟩"
        result_num = 0
    elif rand <= 503:
        result_color = "czerwony"
        result_emoji = "🟥"
        result_num = random.choice([1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36])
    else:
        result_color = "czarny"
        result_emoji = "⬛"
        result_num = random.choice([2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35])

    # Sprawdzanie wygranej
    win = False
    multiplier = 0

    if bet_type == result_color:
        win = True
        multiplier = 10 if result_color == "zielony" else 2
    elif bet_type == "parzyste" and result_num != 0 and result_num % 2 == 0:
        win = True
        multiplier = 2
    elif bet_type == "nieparzyste" and result_num != 0 and result_num % 2 != 0:
        win = True
        multiplier = 2

    # Rozliczenie punktów
    d = self.bot.get_user(self.user_id)
    if win:
        prize = self.amount * (multiplier - 1)
        d["points"] += prize
        status = "WYGRANA! 🎉"
        color_embed = 0x2ecc71 # Zielony
    else:
        d["points"] -= self.amount
        status = "PRZEGRANA"
        color_embed = 0xe74c3c # Czerwony
    
    self.bot.save_data()

    # Wynik końcowy w Embedzie dla lepszego wyglądu
    embed = discord.Embed(title=f"🎰 Wynik: {status}", color=color_embed)
    embed.description = f"Wypadło: {result_emoji} **{result_color.upper()}** ({result_num})"
    
    if win:
        embed.add_field(name="Nagroda", value=f"+{self.amount * multiplier:.1f} pkt")
    else:
        embed.add_field(name="Strata", value=f"-{self.amount:.1f} pkt")
    
    embed.set_footer(text=f"Twoje saldo: {d['points']:.1f} pkt")

    await interaction.edit_original_response(content=None, embed=embed)
