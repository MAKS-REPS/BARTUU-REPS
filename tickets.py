import discord
from discord import ui

# --- KONFIGURACJA ZAKTUALIZOWANA ---
ID_KATEGORII_TICKETOW = 1503426695787708608  # Twoje nowe ID
REQUIRED_ROLE_ID = 1500979741191180318
BARTUU_BLUE = 0x3498db

class TicketMenu(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="POMOC", description="Ogólna pomoc i pytania", emoji="❓"),
            discord.SelectOption(label="POMOC Z ZAMÓWIENIEM", description="Kliknij, jeśli potrzebujesz pomocy z zamówieniem", emoji="🛒"),
            discord.SelectOption(label="PROBLEM Z SHIPPINGIEM", description="Kliknij, jeśli masz problem z shippingiem", emoji="🚛"),
        ]
        super().__init__(
            placeholder="❌ Nie wybrano żadnej z kategorii", 
            min_values=1, 
            max_values=1, 
            options=options, 
            custom_id="persistent_ticket_select"
        )

    async def callback(self, interaction: discord.Interaction):
        # 1. Informujemy Discorda, że pracujemy nad odpowiedzią (zapobiega błędowi interakcji)
        await interaction.response.defer(ephemeral=True)
        
        guild = interaction.guild
        category = guild.get_channel(ID_KATEGORII_TICKETOW)
        admin_role = guild.get_role(REQUIRED_ROLE_ID)
        
        if not category:
            return await interaction.followup.send("❌ Błąd: Nie znaleziono kategorii ticketów. Sprawdź ID.", ephemeral=True)
        
        if not admin_role:
            return await interaction.followup.send("❌ Błąd: Nie znaleziono roli administracyjnej.", ephemeral=True)

        # Ustawienia uprawnień dla kanału
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True, read_message_history=True),
            admin_role: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True, read_message_history=True)
        }
        
        try:
            # 2. Tworzenie kanału
            channel = await guild.create_text_channel(
                name=f"ticket-{interaction.user.name}", 
                category=category, 
                overwrites=overwrites
            )
            
            embed = discord.Embed(
                title="🎫 BARTUU REPS × TICKET", 
                description=f"Witaj {interaction.user.mention}!\nWybrałeś kategorię: **{self.values[0]}**.\nZaraz ktoś z administracji Ci pomoże.", 
                color=BARTUU_BLUE
            )
            embed.set_footer(text="System Ticketów • Bartuu Reps")
            
            await channel.send(content=f"{interaction.user.mention} | {admin_role.mention}", embed=embed)
            
            # 3. Wysyłamy potwierdzenie używając followup, bo wcześniej użyliśmy defer
            await interaction.followup.send(f"✅ Otwarto ticket: {channel.mention}", ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Wystąpił błąd podczas tworzenia kanału: {e}", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # View będzie działać nawet po restarcie bota
        self.add_item(TicketMenu())

# --- PRZYKŁAD UŻYCIA W KOMENDZIE ---
# Aby wysłać menu na kanał, użyj:
# await ctx.send("Wybierz kategorię, aby otworzyć ticket:", view=TicketView())
