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

# --- KONFIGURACJA (ZAKTUALIZOWANE ID) ---
WELCOME_CHANNEL_ID = 1500979786103652365
BARTUU_BLUE = 0x3498db

ROLE_FILMY_ID = 1500979752368996392
ROLE_PROMOCJE_ID = 1500979750762451017

intents = discord.Intents.all()

class BartuuBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Rejestracja widoków (aby przyciski działały po restarcie bota)
        # Przekazujemy ID ról do RoleView, aby system pingów działał poprawnie
        self.add_view(RoleView(ROLE_FILMY_ID, ROLE_PROMOCJE_ID))
        self.add_view(TicketView())
        
        # Inicjalizacja komendy embed
        await setup_embed_command(self, None, BARTUU_BLUE)
        
        # Synchronizacja komend slash
        await self.tree.sync()
        print(f"✅ System BARTUU REPS gotowy. Komendy zsynchronizowane.")

bot = BartuuBot()

@bot.event
async def on_ready():
    print(f"🚀 Zalogowano jako: {bot.user}")
    print(f"📌 Kanał Welcome: {WELCOME_CHANNEL_ID}")
    print(f"📌 Rola Filmy: {ROLE_FILMY_ID}")
    print(f"📌 Rola Promocje: {ROLE_PROMOCJE_ID}")

# --- POWITANIA ---
@bot.event
async def on_member_join(member):
    await handle_welcome(member, WELCOME_CHANNEL_ID, BARTUU_BLUE)

# --- KOMENDA /ID (DOSTĘPNA DLA WSZYSTKICH) ---
@bot.tree.command(name="id", description="Sprawdź ID swoje, oznaczonej osoby, roli lub kanału")
@app_commands.describe(
    uzytkownik_lub_rola="Oznacz osobę lub rolę, której ID chcesz poznać",
    kanal="Wybierz kanał z listy"
)
async def get_id(
    interaction: discord.Interaction, 
    uzytkownik_lub_rola: typing.Optional[typing.Union[discord.Member, discord.Role]] = None,
    kanal: typing.Optional[discord.abc.GuildChannel] = None
):
    # Jeśli użytkownik nic nie wybrał, bot pokazuje ID osoby wpisującej komendę
    target = uzytkownik_lub_rola or kanal or interaction.user
    
    # Określanie typu obiektu
    if isinstance(target, discord.Member): typ = "Użytkownik"
    elif isinstance(target, discord.Role): typ = "Rola"
    elif isinstance(target, discord.TextChannel): typ = "Kanał tekstowy"
    elif isinstance(target, discord.CategoryChannel): typ = "Kategoria"
    elif isinstance(target, discord.VoiceChannel): typ = "Kanał głosowy"
    elif isinstance(target, discord.Thread): typ = "Wątek"
    else: typ = "Obiekt"

    embed = discord.Embed(
        title="🆔 Informacje o ID",
        description="Poniżej znajdują się dane wybranego obiektu:",
        color=BARTUU_BLUE
    )
    
    nazwa = target.mention if hasattr(target, 'mention') else target.name
    embed.add_field(name="Nazwa / Oznaczenie", value=nazwa, inline=False)
    embed.add_field(name="ID", value=f"`{target.id}`", inline=True)
    embed.add_field(name="Typ", value=typ, inline=True)
    
    embed.set_footer(text=f"ID Serwera: {interaction.guild.id} | Wywołane przez: {interaction.user.display_name}")

    # Ustawione na ephemeral=True, aby nie śmiecić na kanale (widoczne tylko dla wywołującego)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- KOMENDA /PANEL (TYLKO DLA ADMINISTRACJI) ---
@bot.tree.command(name="panel", description="Wysyła panel do zarządzania ticketami lub rolami")
@app_commands.default_permissions(administrator=True)
@app_commands.choices(typ=[
    app_commands.Choice(name="Tickety (Pomoc/Dostęp)", value="tickets"),
    app_commands.Choice(name="Role (Powiadomienia)", value="roles")
])
async def panel(interaction: discord.Interaction, typ: app_commands.Choice[str]):
    if typ.value == "tickets":
        embed = discord.Embed(
            title="🚨 BARTUU REPS × CENTRUM POMOCY", 
            description="**Wybierz kategorię z menu poniżej, aby otworzyć zgłoszenie.**\nNasz zespół pomoże Ci najszybciej jak to możliwe.", 
            color=BARTUU_BLUE
        )
        await interaction.response.send_message(embed=embed, view=TicketView())
    
    elif typ.value == "roles":
        embed = discord.Embed(
            title="☀️ BARTUU REPS × POWIADOMIENIA",
            description=(
                "**Wybierz role, które Cię interesują:**\n\n"
                f"🎁 <@&{ROLE_PROMOCJE_ID}> — info o dropach i okazjach\n"
                f"🎬 <@&{ROLE_FILMY_ID}> — info o nowych filmach"
            ),
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, view=RoleView(ROLE_FILMY_ID, ROLE_PROMOCJE_ID))

# --- URUCHOMIENIE ---
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
