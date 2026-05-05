import discord

# --- KONFIGURACJA ZAKTUALIZOWANA ---
ID_KATEGORII_TICKETOW = 1500979781066297394
REQUIRED_ROLE_ID = 1500979741191180318
BARTUU_BLUE = 0x3498db

class TicketMenu(discord.ui.Select):
    def __init__(self):
        # Usunięto opcję "DOSTĘP"
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
        guild = interaction.guild
        category = guild.get_channel(ID_KATEGORII_TICKETOW)
        admin_role = guild.get_role(REQUIRED_ROLE_ID)
        
        if not category:
            return await interaction.response.send_message("❌ Błąd: Nie znaleziono kategorii ticketów.", ephemeral=True)
        
        if not admin_role:
            return await interaction.response.send_message("❌ Błąd: Nie znaleziono roli administracyjnej.", ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            admin_role: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True)
        }
        
        # Tworzenie kanału
        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}", 
            category=category, 
            overwrites=overwrites
        )
        
        # Nazwa zmieniona na BARTUU REPS
        embed = discord.Embed(
            title="🎫 BARTUU REPS × TICKET", 
            description=f"Witaj {interaction.user.mention}!\nWybrałeś kategorię: **{self.values[0]}**.\nZaraz ktoś z administracji Ci pomoże.", 
            color=BARTUU_BLUE
        )
        
        await channel.send(content=f"{interaction.user.mention} | {admin_role.mention}", embed=embed)
        await interaction.response.send_message(f"✅ Otwarto ticket: {channel.mention}", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketMenu())
