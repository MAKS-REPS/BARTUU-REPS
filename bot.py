import discord
from discord import app_commands
from discord.ext import commands
import os
import typing

# --- IMPORTY TWOICH MODUŁÓW ---
from welcome import handle_welcome
from roles import RoleView
from tickets import TicketView
from embeds import setup_embed_command

# --- KONFIGURACJA ID ---
WELCOME_CHANNEL_ID = 1505327306531668099
BARTUU_BLUE = 0x3498db

ROLE_FILMY_ID = 1505327273912303616
ROLE_PROMOCJE_ID = 1505327272792690718

# ROLE Z UPRAWNIENIAMI (OWNER, ADMIN, SUPPORT)
ALLOWED_ROLES = [
    1505327259123322890, # Owner
    1505327260658302976, # Admin
    1505327262847991839  # Support
]

intents = discord.Intents.all()

class BartuuBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Rejestracja widoków dla trwałości przycisków
        self.add_view(RoleView(ROLE_FILMY_ID, ROLE_PROMOCJE_ID))
        self.add_view(TicketView())
        
        # Inicjalizacja komendy embed
        await setup_embed_command(self, None, BARTUU_BLUE)
        
        await self.tree.sync()
        print(f"✅ System BARTUU REPS gotowy.")

bot = BartuuBot()

# --- FUNKCJA SPRAWDZAJĄCA UPRAWNIENIA ---
def has_permission(interaction: discord.Interaction):
    user_role_ids = [role.id for role in interaction.user.roles]
    return any(role_id in user_role_ids for role_id in ALLOWED_ROLES)

@bot.event
async def on_ready():
    print(f"🚀 Zalogowano jako: {bot.user}")

# --- POWITANIA ---
@bot.event
async def on_member_join(member):
    await handle_welcome(member, WELCOME_CHANNEL_ID, BARTUU_BLUE)

# --- KOMENDA /ID (TYLKO DLA OWNER/ADMIN/SUPPORT) ---
@bot.tree.command(name="id", description="Sprawdź ID swoje, osoby, roli lub kanału")
@app_commands.describe(uzytkownik_lub_rola="Oznacz cel", kanal="Wybierz kanał")
async def get_id(
    interaction: discord.Interaction, 
    uzytkownik_lub_rola: typing.Optional[typing.Union[discord.Member, discord.Role]] = None,
    kanal: typing.Optional[discord.abc.GuildChannel] = None
):
    if not has_permission(interaction):
        return await interaction.response.send_message("❌ Nie masz uprawnień do używania tej komendy.", ephemeral=True)

    target = uzytkownik_lub_rola or kanal or interaction.user
    
    embed = discord.Embed(title="🆔 Informacje o ID", color=BARTUU_BLUE)
    nazwa = target.mention if hasattr(target, 'mention') else target.name
    embed.add_field(name="Nazwa / Oznaczenie", value=nazwa, inline=False)
    embed.add_field(name="ID", value=f"`{target.id}`", inline=True)
    embed.set_footer(text=f"Wywołane przez: {interaction.user.display_name}")

    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- KOMENDA /PANEL (TYLKO DLA OWNER/ADMIN/SUPPORT) ---
@bot.tree.command(name="panel", description="Wybierz typ panelu do wysłania")
@app_commands.choices(typ=[
    app_commands.Choice(name="Tickety (Pomoc/Dostęp)", value="tickets"),
    app_commands.Choice(name="Role: Wszystko", value="roles_all"),
    app_commands.Choice(name="Role: Tylko Promocje", value="roles_promo"),
    app_commands.Choice(name="Role: Tylko Filmy (TikTok)", value="roles_tiktok")
])
async def panel(interaction: discord.Interaction, typ: app_commands.Choice[str]):
    if not has_permission(interaction):
        return await interaction.response.send_message("❌ Nie masz uprawnień do wysyłania paneli.", ephemeral=True)

    wybor = typ.value

    if wybor == "tickets":
        embed = discord.Embed(
            title="🚨 BARTUU REPS × CENTRUM POMOCY", 
            description="**Wybierz kategorię z menu poniżej, aby otworzyć zgłoszenie.**", 
            color=BARTUU_BLUE
        )
        await interaction.response.send_message(embed=embed, view=TicketView())
    
    elif wybor == "roles_all":
        # Formatowanie zgodne z image_3.png
        embed = discord.Embed(
            title="☀️ BARTUU REPS × WYBIERZ PINGI",
            description=(
                "🎁 **Ping Promocje**\n"
                "→ Otrzymuj powiadomienia o promocjach!\n\n"
                "🎬 **Ping Filmy**\n"
                "→ Otrzymuj powiadomienia o nowych filmach!"
            ),
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, view=RoleView(ROLE_FILMY_ID, ROLE_PROMOCJE_ID))

    elif wybor == "roles_promo":
        embed = discord.Embed(
            title="🎁 Ping Promocje",
            description="→ Otrzymuj powiadomienia o promocjach!",
            color=discord.Color.red()
        )
        view = RoleView(ROLE_FILMY_ID, ROLE_PROMOCJE_ID)
        view.clear_items()
        view.add_item(discord.ui.Button(label="Ping Promocje", style=discord.ButtonStyle.success, emoji="🎁", custom_id="role_promocje_btn"))
        await interaction.response.send_message(embed=embed, view=view)

    elif wybor == "roles_tiktok":
        embed = discord.Embed(
            title="🎬 Ping Filmy",
            description="→ Otrzymuj powiadomienia o nowych filmach!",
            color=discord.Color.red()
        )
        view = RoleView(ROLE_FILMY_ID, ROLE_PROMOCJE_ID)
        view.clear_items()
        view.add_item(discord.ui.Button(label="Ping TikTok", style=discord.ButtonStyle.secondary, emoji="🎬", custom_id="role_filmy_btn"))
        await interaction.response.send_message(embed=embed, view=view)

# --- URUCHOMIENIE ---
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
