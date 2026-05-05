import discord
from discord import app_commands

async def setup_embed_command(bot, REQUIRED_ROLE_ID, Bartuu_BLUE):
    @bot.tree.command(name="embed", description="Wysyła spersonalizowany komunikat w ramce (Embed)")
    @app_commands.default_permissions(administrator=True) # Widoczne tylko dla adminów
    @app_commands.describe(
        tytul="Nagłówek wiadomości",
        opis="Treść (możesz oznaczać role używając <@&ID_ROLI>)",
        kolor="Kolor paska HEX (np. #ff0000 lub zostaw puste)"
    )
    async def create_embed(interaction: discord.Interaction, tytul: str, opis: str, kolor: str = None):
        # Sprawdzenie uprawnień administratora
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Brak uprawnień do używania tej komendy.", ephemeral=True)

        # Logika koloru
        if kolor:
            try:
                hex_str = kolor.replace("#", "")
                embed_color = int(hex_str, 16)
            except ValueError:
                return await interaction.response.send_message("❌ Błędny format koloru HEX!", ephemeral=True)
        else:
            embed_color = Bartuu_BLUE

        # Obsługa formatowania tekstu
        format_opis = opis.replace("\\n", "\n")
        
        new_embed = discord.Embed(
            title=tytul,
            description=format_opis,
            color=embed_color
        )
        
        # Sekcja set_footer została całkowicie usunięta

        # Wysłanie potwierdzenia (widoczne tylko dla wywołującego)
        await interaction.response.send_message("✅ Embed wysłany!", ephemeral=True)
        
        # Wysłanie właściwego embeda na kanał
        await interaction.channel.send(embed=new_embed)
