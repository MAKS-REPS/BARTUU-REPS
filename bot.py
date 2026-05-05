import discord
from discord import app_commands
from discord.ext import commands
import os

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
        
        # Inicjalizacja komendy embed (None zamiast ID roli, bo używamy Admina)
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

# --- KOMENDA /PANEL (Z POPRAWIONYM MENU WYBORU) ---
@bot.tree.command(name="panel", description="Wybierz typ panelu do wysłania")
@app_commands.default_permissions(administrator=True)
@app_commands.choices(typ=[
    app_commands.Choice(name="Tickety (Pomoc/Dostęp)", value="tickets"),
    app_commands.Choice(name="Role (Pingi)", value="roles")
])
async def panel(interaction: discord.Interaction, typ: app_commands.Choice[str]):
    # Pobieramy wartość wybraną z menu (value)
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
# Token brany z Railway Variables
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
