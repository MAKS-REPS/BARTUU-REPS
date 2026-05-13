import discord

class RoleView(discord.ui.View):
    def __init__(self, role_filmy_id, role_promocje_id):
        # timeout=None sprawia, że przyciski działają nawet po restarcie bota
        super().__init__(timeout=None)
        self.role_filmy_id = role_filmy_id
        self.role_promocje_id = role_promocje_id

    async def toggle_role(self, interaction: discord.Interaction, role_id: int):
        role = interaction.guild.get_role(role_id)
        
        # Zabezpieczenie na wypadek błędu w ID
        if not role:
            return await interaction.response.send_message("❌ Nie znaleziono tej roli na serwerze. Skontaktuj się z administratorem.", ephemeral=True)

        if role in interaction.user.roles:
            try:
                await interaction.user.remove_roles(role)
                await interaction.response.send_message(f"❌ Usunięto rolę {role.mention}", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("❌ Bot nie ma uprawnień do usuwania ról. Sprawdź hierarchię ról!", ephemeral=True)
        else:
            try:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(f"✅ Nadano rolę {role.mention}", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("❌ Bot nie ma uprawnień do nadawania ról. Sprawdź hierarchię ról!", ephemeral=True)

    @discord.ui.button(label="Ping Promocje", style=discord.ButtonStyle.success, emoji="🎁", custom_id="role_promocje_btn")
    async def promocje(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, self.role_promocje_id)

    @discord.ui.button(label="Ping Filmy", style=discord.ButtonStyle.primary, emoji="🎬", custom_id="role_filmy_btn")
    async def filmy(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, self.role_filmy_id)
