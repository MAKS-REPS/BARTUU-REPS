import discord

# Funkcja obsługująca powitania, przyjmuje parametry z bot.py
async def handle_welcome(member, channel_id, color_hex):
    # Pobieramy kanał z serwera na podstawie ID
    channel = member.guild.get_channel(channel_id)
    
    if channel:
        # Pobieramy aktualną liczbę osób na serwerze
        count = member.guild.member_count
        
        # Tworzymy embed powitalny
        embed = discord.Embed(
            title="👋 BARTUU REPS × WITAMY",
            description=(
                f"• 🤱 × Witaj {member.mention} na **BARTUU REPS**\n"
                f"• 👥 × Jesteś **{count} osobą** na naszym serwerze!\n"
                f"• ✨ × Liczymy, że zostaniesz z nami na dłużej!"
            ),
            color=color_hex  # Używa koloru zdefiniowanego w bot.py (BARTUU_BLUE)
        )
        
        # Ustawienie zdjęcia profilowego użytkownika jako miniatury
        embed.set_thumbnail(url=member.display_avatar.url)
        
        # Opcjonalnie: zdjęcie w stopce lub banner (jeśli posiadasz URL)
        embed.set_footer(text="System Powitań • Bartuu Reps", icon_url=member.guild.icon.url if member.guild.icon else None)
        
        try:
            await channel.send(content=f"Witaj {member.mention}!", embed=embed)
        except discord.Forbidden:
            print(f"❌ Błąd: Bot nie ma uprawnień do wysyłania wiadomości na kanale {channel_id}.")
