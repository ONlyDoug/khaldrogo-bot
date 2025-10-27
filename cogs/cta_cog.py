import discord
from discord import app_commands # IMPORTAÇÃO ADICIONADA
from discord.ext import commands
from discord.ui import Modal, InputText
from discord import InputTextStyle, Option, Forbidden, utils

# --- 1. Definição do Modal (Formulário) ---
# (O código da classe CTAModal permanece IDÊNTICO)
class CTAModal(Modal):
    def __init__(self, bot, target_channel_id: int, cta_type: str):
        super().__init__(title="Criar Nova CTA")
        self.bot = bot
        self.target_channel_id = target_channel_id
        if cta_type == "obrigatoria":
            self.cta_type_display = "Obrigatória"
            self.embed_color = discord.Colour.red()
        else:
            self.cta_type_display = "Opcional"
            self.embed_color = discord.Colour.blue()
        self.add_item(InputText( label="Título da CTA", placeholder="Ex: Defesa de Território em Lymhurst", max_length=100))
        self.add_item(InputText( label="Data e Hora", placeholder="Ex: 21/10 às 20:00 BRT (Formar 19:30)", max_length=100))
        self.add_item(InputText( label="Observações (Opcional)", placeholder="Ex: T8.3 equivalente. Trazer comida e poções.", style=InputTextStyle.paragraph, required=False))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("Processando sua CTA...", ephemeral=True)
        target_channel = self.bot.get_channel(self.target_channel_id)
        if not target_channel:
            await interaction.followup.send(f"Erro Crítico: Canal de CTA (ID: {self.target_channel_id}) não foi encontrado.", ephemeral=True)
            return
        embed = discord.Embed( title=f"📢 {self.inputs[0].value}", description=f"**Data/Hora:** {self.inputs[1].value}\n**Tipo:** {self.cta_type_display}", color=self.embed_color)
        if self.inputs[2].value:
            embed.add_field(name="Observações", value=self.inputs[2].value, inline=False)
        embed.set_footer(text=f"CTA criada por: {interaction.user.display_name}")
        if interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)
        try:
            msg = await target_channel.send(content="@everyone Nova CTA!", embed=embed)
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
            await msg.add_reaction("❓")
            await interaction.followup.send(f"CTA '{self.inputs[0].value}' criada com sucesso em {target_channel.mention}!", ephemeral=True)
        except Forbidden:
            await interaction.followup.send(f"Erro: Não tenho permissão para enviar mensagens ou adicionar reações em {target_channel.mention}.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Ocorreu um erro inesperado ao enviar a CTA: {e}", ephemeral=True)
            print(f"Erro ao processar CTA Modal: {e}")

# --- 5. Definição da Cog (Módulo) ---
class CTACog(commands.Cog):
    """Módulo responsável pela funcionalidade de Gestão de CTAs."""
    
    def __init__(self, bot):
        self.bot = bot
        print(">>> cta_cog.py FOI LIDO E INICIADO <<<")

    # ----- MUDANÇA CRÍTICA AQUI -----
    @app_commands.command(
        name="cta",
        description="Cria uma nova chamada para ZvZ (Apenas Oficiais)"
    )
    @app_commands.checks.has_permissions(manage_guild=True) # MUDANÇA AQUI
    @app_commands.describe(tipo="Qual o tipo de CTA?") # MUDANÇA AQUI
    async def cta(
        self,
        interaction: discord.Interaction, # MUDANÇA AQUI
        tipo: commands.Range[str, 1, -1], # MUDANÇA AQUI
    ):
        """Comando principal que abre o formulário de CTA."""
        
        # MUDANÇA AQUI: `choices` não é mais um parâmetro do decorador
        if tipo not in ["obrigatoria", "opcional"]:
             await interaction.response.send_message("Tipo inválido. Use 'obrigatoria' ou 'opcional'.", ephemeral=True)
             return

        if tipo == "obrigatoria":
            channel_name = "❗ | cta-obrigatória"
        else:
            channel_name = "⚔️ | cta-opcional"

        # MUDANÇA AQUI: `interaction.guild`
        target_channel = utils.get(interaction.guild.text_channels, name=channel_name)
        
        if not target_channel:
            # MUDANÇA AQUI: `interaction.response.send_message`
            await interaction.response.send_message(
                f"Erro: O canal `#{channel_name}` não foi encontrado."
                f"Execute o `/setup-servidor` primeiro.",
                ephemeral=True
            )
            return
        
        modal = CTAModal(bot=self.bot, target_channel_id=target_channel.id, cta_type=tipo)
        # MUDANÇA AQUI: `interaction.response.send_modal`
        await interaction.response.send_modal(modal)

    @cta.error
    async def cta_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Handler de erro específico para o /cta."""
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("Apenas Oficiais e Líderes podem usar este comando.", ephemeral=True)
        else:
            send_func = interaction.followup.send if interaction.response.is_done() else interaction.response.send_message
            await send_func(f"Ocorreu um erro inesperado: {error}", ephemeral=True)
            print(f"Erro no comando '/cta': {error}")

# --- 7. Função de Setup (Obrigatória para Cogs) ---
async def setup(bot):
    await bot.add_cog(CTACog(bot))