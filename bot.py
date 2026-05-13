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

# --- KONFIGURACJA ---
WELCOME_CHANNEL_ID = 1500979786103652365
BARTUU_BLUE = 0x3498db

ROLE_FILMY_ID = 1500979752368996392
ROLE_PROMOCJE_ID = 1500979750762451017

# ROLE Z UPRAWNIENIAMI DO KOMEND ADMINA
ALLOWED_ROLES = [
    1500979741191180318, # Owner
    1501274158628343978, # Dev
    1500979743040737412  # Support
]

intents = discord.Intents.all()

class BartuuBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_view(RoleView(ROLE_FILMY_ID, ROLE_PROMOCJE_ID))
        self.add_view(TicketView())
        await setup_embed_command(self, None, BARTUU_BLUE)
        await self.tree.sync()
        print(f"✅ System BARTUU REPS gotowy.")

bot = BartuuBot()

# FUNKCJA POMOCNICZA DO SPRAWDZANIA RÓL
def has_permission(interaction: discord.Interaction):
    user_role_ids = [role.id for role in interaction.user.roles]
    return any(role_id in user_role_ids for role_id in ALLOWED_ROLES)

@bot.event
async def on_ready():
    print(f"🚀 Zalogowano jako: {bot.user}")

@bot.event
async def on_member_join(member):
    await handle_welcome(member, WELCOME_CHANNEL_ID, BARTUU_BLUE)

# --- KOMENDA /ID (TYLKO DLA OWNER/DEV/SUPPORT) ---
@bot.tree.command(name="id", description="Sprawdź ID swoje, oznaczonej osoby, roli lub kanału")
@app_commands.describe(
    uzytkownik_lub_rola="Oznacz osobę lub rolę",
    kanal="Wybierz kanał"
)
async def get_id(
    interaction: discord.Interaction, 
    uzytkownik_lub_rola: typing.Optional[typing.Union[discord.Member, discord.Role]] = None,
    kanal: typing.Optional[discord.abc.GuildChannel] = None
):
    if not has_permission(interaction):
        return await interaction.response.send_message("❌ Nie masz uprawnień do tej komendy.", ephemeral=True)

    target = uzytkownik_lub_rola or kanal or interaction.user
    
    types = {
        discord.Member: "Użytkownik",
        discord.Role: "Rola",
        discord.TextChannel: "Kanał tekstowy",
        discord.CategoryChannel: "Kategoria",
        discord.VoiceChannel: "Kanał głosowy",
        discord.Thread: "Wątek"
    }

    typ_nazwa = "Obiekt"
    for cls, name in types.items():
        if isinstance(target, cls):
            typ_nazwa = name
            break

    embed = discord.Embed(title="🆔 Informacje o ID", color=BARTUU_BLUE)
    nazwa = target.mention if hasattr(target, 'mention') else target.name
    embed.add_field(name="Nazwa / Oznaczenie", value=nazwa, inline=False)
    embed.add_field(name="ID", value=f"`{target.id}`", inline=True)
    embed.add_field(name="Typ", value=typ_nazwa, inline=True)
    embed.set_footer(text=f"ID Serwera: {interaction.guild.id}")

    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- KOMENDA /PANEL (TYLKO DLA OWNER/DEV/SUPPORT) ---
@bot.tree.command(name="panel", description="Wybierz typ panelu do wysłania")
@app_commands.choices(typ=[
    app_commands.Choice(name="Tickety (Pomoc/Dostęp)", value="tickets"),
    app_commands.Choice(name="Role: Wszystko", value="roles_all"),
    app_commands.Choice(name="Role: Tylko Promocje", value="roles_promo"),
    app_commands.Choice(name="Role: Tylko Filmy (TikTok)", value="roles_tiktok")
])
async def panel(interaction: discord.Interaction, typ: app_commands.Choice[str]):
    if not has_permission(interaction):
        return await interaction.response.send_message("❌ Nie masz uprawnień do tej komendy.", ephemeral=True)

    wybor = typ.value

    if wybor == "tickets":
        embed = discord.Embed(
            title="🚨 BARTUU REPS × CENTRUM POMOCY", 
            description="**Wybierz kategorię z menu poniżej, aby otworzyć zgłoszenie.**", 
            color=BARTUU_BLUE
        )
        await interaction.response.send_message(embed=embed, view=TicketView())
    
    elif wybor == "roles_all":
        embed = discord.Embed(
            title="☀️ BARTUU REPS × POWIADOMIENIA",
            description=f"🎁 <@&{ROLE_PROMOCJE_ID}>\n🎬 <@&{ROLE_FILMY_ID}>",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, view=RoleView(ROLE_FILMY_ID, ROLE_PROMOCJE_ID))

    elif wybor == "roles_promo":
        embed = discord.Embed(title="🎁 POWIADOMIENIA × PROMOCJE", description="Kliknij przycisk poniżej.", color=discord.Color.green())
        view = RoleView(ROLE_FILMY_ID, ROLE_PROMOCJE_ID)
        view.clear_items()
        view.add_item(discord.ui.Button(label="Ping Promocje", style=discord.ButtonStyle.success, emoji="🎁", custom_id="role_promocje_btn"))
        await interaction.response.send_message(embed=embed, view=view)

    elif wybor == "roles_tiktok":
        embed = discord.Embed(title="🎬 POWIADOMIENIA × FILMY", description="Kliknij przycisk poniżej.", color=discord.Color.blue())
        view = RoleView(ROLE_FILMY_ID, ROLE_PROMOCJE_ID)
        view.clear_items()
        view.add_item(discord.ui.Button(label="Ping Filmy", style=discord.ButtonStyle.primary, emoji="🎬", custom_id="role_filmy_btn"))
        await interaction.response.send_message(embed=embed, view=view)

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
