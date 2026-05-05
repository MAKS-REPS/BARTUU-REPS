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
# Zaktualizowane ID (konwertowane na liczby)
WELCOME_CHANNEL_ID = 1500979786103652365
REQUIRED_ROLE_ID = 1457769309735485450 # Tutaj zostawiłem poprzednie ID, bo nie podałeś nowego dla roli admina
BARTUU_BLUE = 0x3498db

ROLE_FILMY_ID = 1500979752368996392   # Dawniej TikTok
ROLE_PROMOCJE_ID = 1500979750762451017

intents = discord.Intents.all()

class BartuuBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Rejestracja widoków (Role i Tickety)
        self.add_view(RoleView(ROLE_FILMY_ID, ROLE_PROMOCJE_ID))
        self.add_view(TicketView())
        
        # Inicjalizacja komendy embed
        await setup_embed_command(self, REQUIRED_ROLE_ID, BARTUU_BLUE)
        
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

# --- KOMENDA /PANEL ---
@bot.tree.command(name="panel", description="Wybierz typ panelu do wysłania")
@app_commands.choices(typ=[
    app_commands.Choice(name="Tickety (Pomoc/Dostęp)", value="tickets"),
    app_commands.Choice(name="Role (Pingi)", value="roles")
])
async def panel(interaction: discord.Interaction, typ: str):
    # Sprawdzanie uprawnień
    if not any(role.id == REQUIRED_ROLE_ID for role in interaction.user.roles):
        return await interaction.response.send_message("❌ Brak uprawnień.", ephemeral=True)

    if typ == "tickets":
        embed = discord.Embed(
            title="🚨 BARTUU REPS × CENTRUM POMOCY", 
            description="**Wybierz kategorię z menu poniżej, aby utworzyć zgłoszenie.**", 
            color=BARTUU_BLUE
        )
        await interaction.response.send_message(embed=embed, view=TicketView())
    
    elif typ == "roles":
        embed = discord.Embed(
            title="☀️ BARTUU REPS × WYBIERZ PINGI",
            description="🎁 **Ping Promocje**\n→ Otrzymuj powiadomienia o promocjach!\n\n🎬 **Ping Filmy**\n→ Otrzymuj powiadomienia o nowych filmach!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, view=RoleView(ROLE_FILMY_ID, ROLE_PROMOCJE_ID))

# --- URUCHOMIENIE ---
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
