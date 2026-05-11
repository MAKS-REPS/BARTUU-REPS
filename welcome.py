import discord

# Pamiętaj, aby w Developer Portal włączyć "Server Members Intent"
async def handle_welcome(member):
    # ID kanału, które podałeś
    WELCOME_CHANNEL_ID = 1500979786103652365
    
    # Pobieramy kanał z serwera
    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
    
    if channel:
        count = member.guild.member_count
        # Ustawiamy kolor (np. niebieski, możesz zmienić na discord.Color.from_rgb lub hex)
        color = discord.Color.blue() 

        embed = discord.Embed(
            title="👋 Bartuu Reps × WITAMY",
            description=(
                f"• 🤱 × Witaj {member.mention} na **Maks Reps**\n"
                f"• 👥 × Jesteś **{count} osobą** na naszym serwerze!\n"
                f"• ✨ × Liczymy, że zostaniesz z nami na dłużej!"
            ),
            color=color
        )
        # Ustawienie miniatury jako awatar użytkownika
        embed.set_thumbnail(url=member.display_avatar.url)
        
        await channel.send(embed=embed)
