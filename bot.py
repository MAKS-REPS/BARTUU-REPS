import discord
from discord import app_commands
from discord.ext import commands
import os
import typing  # Dodane dla obsługi wielu typów w komendzie ID

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

intents = discord.Intents.all()

class BartuuBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Rejestracja widoków (aby przyciski działały po restarcie)
        self.add_view(RoleView(ROLE_FILMY_ID, ROLE_PROMOCJE_ID))
        self.add_view(TicketView())
        
        # Inicjalizacja komendy embed
        await setup_embed_command(self, None, BARTUU_BLUE)
        
        await self.tree.sync()
        print(f"✅ Bot {self.user} gotowy. System BARTUU REPS załadowany.")

bot = BartuuBot()

@bot.event
async def on_ready():
    print(f"🚀 Zalogowano jako: {bot.user}")

# --- POWITANIA ---
@bot.event
async def on_member_join(member):
    await handle_welcome(member, WELCOME_CHANNEL_ID, BARTUU_BLUE)

# --- KOMENDA /ID (NOWA) ---
@bot.tree.command(name="id", description="Pobiera ID użytkownika, roli lub kanału")
@app_commands.describe(obiekt="Oznacz kogoś, rolę lub kanał (puste = ID obecnego kanału)")
@app_commands.default_permissions(administrator=True) # Tylko admin może sprawdzać ID
async def get_id(interaction: discord.Interaction, obiekt: typing.Union[discord.Member, discord.Role, discord.TextChannel, discord.CategoryChannel, discord.VoiceChannel] = None):
    if obiekt is None:
        # Jeśli nic nie wybrano, podaj ID kanału i serwera
        embed = discord.Embed(title="📍 ID Lokalizacji", color=BARTUU_BLUE)
        embed.add_field(name="Kanał", value=f"`{interaction.channel.id}`", inline=True)
        embed.add_field(name="Serwer", value=f"`{interaction.guild.id}`", inline=True)
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    # Logika sprawdzania typu obiektu
    typ = "Obiekt"
    if isinstance(obiekt, discord.Member): typ = "Użytkownik"
    elif isinstance(obiekt, discord.Role): typ = "Rola"
    elif isinstance(obiekt, discord.TextChannel): typ = "Kanał tekstowy"
    elif isinstance(obiekt, discord.CategoryChannel): typ = "Kategoria"
    elif isinstance(obiekt, discord.VoiceChannel): typ = "Kanał głosowy"

    embed = discord.Embed(
        title=f"🆔 Informacje: {obiekt.name}",
        description=f"**Typ:** {typ}\n**ID:** `{obiekt.id}`",
        color=BARTUU_BLUE
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- KOMENDA /PANEL ---
@bot.tree.command(name="panel", description="Wybierz typ panelu do wysłania")
@app_commands.default_permissions(administrator=True)
@app_commands.choices(typ=[
    app_commands.Choice(name="Tickety (Pomoc/Dostęp)", value="tickets"),
    app_commands.Choice(name="Role (Pingi)", value="roles")
])
async def panel(interaction: discord.Interaction, typ: app_commands.Choice[str]):
    wybor = typ.value

    if wybor == "tickets":
        embed = discord.Embed(
            title="🚨 BARTUU REPS × CENTRUM POMOCY", 
            description="**Wybierz kategorię z menu poniżej, aby utworzyć zgłoszenie.**", 
            color=BARTUU_BLUE
        )
        await interaction.response.send_message(embed=embed, view=TicketView())
    
    elif wybor == "roles":
        embed = discord.Embed(
            title="☀️ BARTUU REPS × WYBIERZ PINGI",
            description="🎁 **Ping Promocje**\n→ Otrzymuj powiadomienia o promocjach!\n\n🎬 **Ping Filmy**\n→ Otrzymuj powiadomienia o nowych filmach!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, view=RoleView(ROLE_FILMY_ID, ROLE_PROMOCJE_ID))

# --- URUCHOMIENIE ---
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
