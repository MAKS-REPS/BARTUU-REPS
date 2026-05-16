import discord
from discord import app_commands

async def setup_embed_command(bot, REQUIRED_ROLE_ID, Bartuu_BLUE):
    @bot.tree.command(name="embed", description="Wysyła spersonalizowany komunikat w ramce (Embed)")
    @app_commands.describe(
        tytul="Nagłówek wiadomości",
        opis="Treść (możesz oznaczać role używając <@&ID_ROLI>)",
        kolor="Kolor paska HEX (np. #ff0000 lub zostaw puste)"
    )
    async def create_embed(interaction: discord.Interaction, tytul: str, opis: str, kolor: str = None):
        # LISTA DOZWOLONYCH ID RÓL (Owner i Admin)
        ALLOWED_ROLES = [1505327259123322890, 1505327260658302976]
        
        # Sprawdzanie czy użytkownik ma którąś z tych ról
        user_role_ids = [role.id for role in interaction.user.roles]
        if not any(role_id in ALLOWED_ROLES for role_id in user_role_ids):
            return await interaction.response.send_message("❌ Brak uprawnień do używania tej komendy.", ephemeral=True)

        if kolor:
            try:
                hex_str = kolor.replace("#", "")
                embed_color = int(hex_str, 16)
            except ValueError:
                return await interaction.response.send_message("❌ Błędny format koloru HEX!", ephemeral=True)
        else:
            embed_color = Bartuu_BLUE

        format_opis = opis.replace("\\n", "\n")
        
        new_embed = discord.Embed(
            title=tytul,
            description=format_opis,
            color=embed_color
        )
        
        await interaction.response.send_message("✅ Embed wysłany!", ephemeral=True)
        await interaction.channel.send(embed=new_embed)
