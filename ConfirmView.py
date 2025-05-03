import discord
from discord.ui import Button, View

class ConfirmView(View):
    def __init__(self, callback_func, timeout=30):
        super().__init__(timeout=timeout)
        self.callback_func = callback_func

    @discord.ui.button(label='✅ Confirm', style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        await self.callback_func(interaction)
        self.stop()

    @discord.ui.button(label='❌ Cancel', style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message('Cancelled.', ephemeral=True)
        self.stop()
