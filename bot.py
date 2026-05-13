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

intents = discord.Intents.all()

class BartuuBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Rejestracja widoków
        self.add_view(RoleView(ROLE_FILMY_ID, ROLE_PROMOCJE_ID))
        self.add_view(TicketView())
        
        # Inicjalizacja komendy embed
        await setup_embed_command(self, None, BARTUU_BLUE)
        
        # Synchronizacja komend
        await self.tree.sync()
        print(f"✅ Komendy zsynchronizowane. Bot {self.user} gotowy.")

bot = BartuuBot()

@bot.event
async def on_ready():
    print(f"🚀 Zalogowano jako: {bot.user}")

# --- POWITANIA ---
@bot.event
async def on_member_join(member):
    await handle_welcome(member, WELCOME_CHANNEL_ID, BARTUU_BLUE)

# --- KOMENDA /ID (WERSJA POPRAWIONA I DZIAŁAJĄCA) ---
@bot.tree.command(name="id", description="Pobiera ID oznaczonego obiektu")
@app_commands.describe(
    oznacz_osobe_lub_role="Wybierz osobę lub rolę",
    wybierz_kanal="Wybierz kanał z listy"
)
@app_commands.default_permissions(administrator=True)
async def get_id(
    interaction: discord.Interaction, 
    oznacz_osobe_lub_role: typing.Optional[typing.Union[discord.Member, discord.Role]] = None,
    wybierz_kanal: typing.Optional[discord.abc.GuildChannel] = None
):
    # Wybieramy co sprawdzić: najpierw osoba/rola, potem kanał, na końcu obecny kanał
    target = oznacz_osobe_lub_role or wybierz_kanal or interaction.channel
    
    # Rozpoznawanie typu dla czytelności
    if isinstance(target, discord.Member): typ = "Użytkownik"
    elif isinstance(target, discord.Role): typ = "Rola"
    elif isinstance(target, discord.TextChannel): typ = "Kanał tekstowy"
    elif isinstance(target, discord.CategoryChannel): typ = "Kategoria"
    elif isinstance(target, discord.VoiceChannel): typ = "Kanał głosowy"
    elif isinstance(target, discord.Thread): typ = "Wątek"
    else: typ = "Obiekt"

    embed = discord.Embed(title="🆔 Informacje o ID", color=BARTUU_BLUE)
    
    # Jeśli to nie kategoria, używamy mention (wzmianki)
    mention_val = target.mention if hasattr(target, 'mention') else target.name
    
    embed.add_field(name="Nazwa/Oznaczenie", value=mention_val, inline=False)
    embed.add_field(name="ID", value=f"`{target.id}`", inline=True)
    embed.add_field(name="Typ", value=typ, inline=True)
    
    # Dodatkowo ID serwera
    embed.set_footer(text=f"ID Serwera: {interaction.guild.id}")

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
