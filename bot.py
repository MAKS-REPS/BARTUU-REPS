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
        # Rejestracja widoków (przyciski)
        self.add_view(RoleView(ROLE_FILMY_ID, ROLE_PROMOCJE_ID))
        self.add_view(TicketView())
        
        # Komenda embed
        await setup_embed_command(self, None, BARTUU_BLUE)
        
        # WYMUSZENIE SYNCHRONIZACJI KOMEND
        await self.tree.sync()
        print(f"✅ Komendy zsynchronizowane globalnie dla każdego użytkownika.")

bot = BartuuBot()

@bot.event
async def on_ready():
    print(f"🚀 Bot {bot.user} działa poprawnie!")

# --- POWITANIA ---
@bot.event
async def on_member_join(member):
    await handle_welcome(member, WELCOME_CHANNEL_ID, BARTUU_BLUE)

# --- KOMENDA /ID (DOSTĘPNA DLA WSZYSTKICH) ---
@bot.tree.command(name="id", description="Sprawdź ID swoje, kogoś, roli lub kanału")
@app_commands.describe(
    uzytkownik_lub_rola="Wybierz osobę lub rolę",
    kanal="Wybierz kanał"
)
# USUNIĘTO: @app_commands.default_permissions(administrator=True) -> Teraz każdy to widzi
async def get_id(
    interaction: discord.Interaction, 
    uzytkownik_lub_rola: typing.Optional[typing.Union[discord.Member, discord.Role]] = None,
    kanal: typing.Optional[discord.abc.GuildChannel] = None
):
    # Logika wyboru celu
    target = uzytkownik_lub_rola or kanal or interaction.user # Jeśli nic nie wybrano, pokaże ID osoby piszącej
    
    # Określanie typu
    if isinstance(target, discord.Member): typ = "Użytkownik"
    elif isinstance(target, discord.Role): typ = "Rola"
    elif isinstance(target, discord.TextChannel): typ = "Kanał tekstowy"
    elif isinstance(target, discord.CategoryChannel): typ = "Kategoria"
    elif isinstance(target, discord.VoiceChannel): typ = "Kanał głosowy"
    else: typ = "Obiekt"

    embed = discord.Embed(
        title="🆔 Informacje o ID",
        description=f"Oto dane obiektu, o który pytałeś:",
        color=BARTUU_BLUE
    )
    
    # Dodawanie pól
    nazwa = target.mention if hasattr(target, 'mention') else target.name
    embed.add_field(name="Nazwa / Oznaczenie", value=nazwa, inline=False)
    embed.add_field(name="ID", value=f"`{target.id}`", inline=True)
    embed.add_field(name="Typ", value=typ, inline=True)
    
    # ID serwera w stopce
    embed.set_footer(text=f"ID Serwera: {interaction.guild.id} | Wywołane przez: {interaction.user.display_name}")

    # ephemeral=False sprawi, że wszyscy będą widzieć odpowiedź (lub True, jeśli tylko pytający)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- KOMENDA /PANEL (TYLKO DLA ADMINA) ---
@bot.tree.command(name="panel", description="Wysyła panel ticketów lub ról")
@app_commands.default_permissions(administrator=True)
@app_commands.choices(typ=[
    app_commands.Choice(name="Tickety", value="tickets"),
    app_commands.Choice(name="Role", value="roles")
])
async def panel(interaction: discord.Interaction, typ: app_commands.Choice[str]):
    if typ.value == "tickets":
        embed = discord.Embed(title="🚨 BARTUU REPS × POMOC", description="Otwórz ticket poniżej.", color=BARTUU_BLUE)
        await interaction.response.send_message(embed=embed, view=TicketView())
    else:
        embed = discord.Embed(title="☀️ BARTUU REPS × ROLE", description="Wybierz swoje powiadomienia.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, view=RoleView(ROLE_FILMY_ID, ROLE_PROMOCJE_ID))

# --- URUCHOMIENIE ---
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
