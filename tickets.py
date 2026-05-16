import discord
from discord import ui

# --- KONFIGURACJA ID ---
ID_KATEGORII_TICKETOW = 1505327302483902607
ID_OWNER = 1505327259123322890
ID_ADMIN = 1505327260658302976
ID_SUPPORT = 1505327262847991839  # Twój nowy ID (zastąpił poprzedni dubel)

BARTUU_BLUE = 0x3498db

class TicketMenu(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="POMOC", description="Ogólna pomoc i pytania", emoji="❓"),
            discord.SelectOption(label="POMOC Z ZAMÓWIENIEM", description="Pomoc z Twoim zamówieniem", emoji="🛒"),
            discord.SelectOption(label="PROBLEM Z SHIPPINGIEM", description="Problemy z dostawą", emoji="🚛"),
        ]
        super().__init__(
            placeholder="Wybierz kategorię zgłoszenia...", 
            min_values=1, 
            max_values=1, 
            options=options, 
            custom_id="persistent_ticket_select"
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        guild = interaction.guild
        category = guild.get_channel(ID_KATEGORII_TICKETOW)
        
        # Pobieranie ról do zmiennych
        owner_role = guild.get_role(ID_OWNER)
        support_role = guild.get_role(ID_SUPPORT)
        admin_role = guild.get_role(ID_ADMIN)
        
        if not category:
            return await interaction.followup.send("❌ Błąd: Kategoria ticketów nie istnieje (sprawdź ID).", ephemeral=True)

        # Ustawienia uprawnień: kto ma widzieć kanał
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }

        # Nadajemy dostęp rolom administracyjnym
        if owner_role: overwrites[owner_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True)
        if support_role: overwrites[support_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True)
        if dev_role: overwrites[dev_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True)
        
        try:
            # Tworzenie kanału
            channel = await guild.create_text_channel(
                name=f"ticket-{interaction.user.name}", 
                category=category, 
                overwrites=overwrites
            )
            
            embed = discord.Embed(
                title="🎫 BARTUU REPS × NOWY TICKET", 
                description=(
                    f"Witaj {interaction.user.mention}!\n\n"
                    f"**Kategoria:** `{self.values[0]}`\n"
                    "Ekipa BARTUU REPS zaraz się Tobą zajmie. Opisz swój problem poniżej.\n\n"
                    "---"
                ), 
                color=BARTUU_BLUE
            )
            embed.set_footer(text="Administracja zostanie powiadomiona.")
            
            # Budowanie stringa z pingami
            pings = [interaction.user.mention]
            if owner_role: pings.append(owner_role.mention)
            if support_role: pings.append(support_role.mention)
            if admin_role: pings.append(admin_role.mention)
            
            # Wysłanie pingu i embeda na nowy kanał
            await channel.send(content=" | ".join(pings), embed=embed)
            
            # Potwierdzenie dla użytkownika
            await interaction.followup.send(f"✅ Ticket utworzony: {channel.mention}", ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Coś poszło nie tak: {e}", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) 
        self.add_item(TicketMenu())
