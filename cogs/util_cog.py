import discord
from discord import app_commands
from discord.ext import commands

class UtilCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print(">>> util_cog.py FOI LIDO E INICIADO <<<")

    @app_commands.command(
        name="ping",
        description="Testa se o bot está vivo e a sincronizar comandos."
    )
    async def ping(self, interaction: discord.Interaction):
        """Responde 'Pong!' para teste."""
        await interaction.response.send_message(
            f"Pong! Latência: {round(self.bot.latency * 1000)}ms", 
            ephemeral=True
        )

# Função obrigatória que o main.py usa para carregar esta Cog
async def setup(bot):
    await bot.add_cog(UtilCog(bot))