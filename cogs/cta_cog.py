import discord
from discord.ext import commands
from discord.ui import Modal, InputText
from discord import InputTextStyle, Option, Forbidden, utils

# --- 1. Definição do Modal (Formulário) ---
class CTAModal(Modal):
    def __init__(self, bot, target_channel_id: int, cta_type: str):
        super().__init__(title="Criar Nova CTA")
        self.bot = bot
        self.target_channel_id = target_channel_id
        
        # Define a cor e o título com base no tipo
        if cta_type == "obrigatoria":
            self.cta_type_display = "Obrigatória"
            self.embed_color = discord.Colour.red()
        else:
            self.cta_type_display = "Opcional"
            self.embed_color = discord.Colour.blue()

        # --- Campos do Formulário ---
        self.add_item(InputText(
            label="Título da CTA",
            placeholder="Ex: Defesa de Território em Lymhurst",
            max_length=100
        ))
        
        self.add_item(InputText(
            label="Data e Hora",
            placeholder="Ex: 21/10 às 20:00 BRT (Formar 19:30)",
            max_length=100
        ))
        
        self.add_item(InputText(
            label="Observações (Opcional)",
            placeholder="Ex: T8.3 equivalente. Trazer comida e poções.",
            style=InputTextStyle.paragraph,
            required=False
        ))

    # --- 2. Lógica de 'Callback' (O que fazer após o 'submit') ---
    async def callback(self, interaction: discord.Interaction):
        """
        Chamado quando o usuário clica em 'Submit' no formulário.
        """
        
        # Resposta imediata (ephemeral) para o Oficial
        await interaction.response.send_message("Processando sua CTA...", ephemeral=True)

        target_channel = self.bot.get_channel(self.target_channel_id)
        if not target_channel:
            await interaction.followup.send(f"Erro Crítico: Canal de CTA (ID: {self.target_channel_id}) não foi encontrado.", ephemeral=True)
            return

        # --- 3. Criação do Embed (Mensagem Formatada) ---
        embed = discord.Embed(
            title=f"📢 {self.inputs[0].value}",
            description=f"**Data/Hora:** {self.inputs[1].value}\n**Tipo:** {self.cta_type_display}",
            color=self.embed_color
        )
        
        # Adiciona o campo de observações apenas se preenchido
        if self.inputs[2].value:
            embed.add_field(name="Observações", value=self.inputs[2].value, inline=False)
        
        embed.set_footer(text=f"CTA criada por: {interaction.user.display_name}")
        
        if interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)

        try:
            # --- 4. Envio e Adição das Reações ---
            # O 'content' @everyone é importante para notificar
            msg = await target_channel.send(content="@everyone Nova CTA!", embed=embed)
            
            # Adiciona as reações conforme o roadmap
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
            await msg.add_reaction("❓")
            
            await interaction.followup.send(f"CTA '{self.inputs[0].value}' criada com sucesso em {target_channel.mention}!", ephemeral=True)
        
        except Forbidden:
            # Erro comum se o bot não tiver permissão no canal de CTA
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

    @commands.slash_command(
        name="cta",
        description="Cria uma nova chamada para ZvZ (Apenas Oficiais)"
    )
    # Restringe a quem pode gerir o servidor (Oficiais/Líderes)
    @commands.has_permissions(manage_guild=True)
    async def cta(
        self,
        ctx: discord.ApplicationContext,
        tipo: Option(str, "Qual o tipo de CTA?", choices=["obrigatoria", "opcional"], required=True),
    ):
        """
        Comando principal que abre o formulário de CTA.
        """
        
        # --- 6. Mapeamento do Canal (Conforme Planta Baixa) ---
        # Encontra o canal de destino correto com base na 'Planta Baixa'
        
        if tipo == "obrigatoria":
            channel_name = "❗ | cta-obrigatória" # 
        else:
            channel_name = "⚔️ | cta-opcional" # 

        # Busca o canal pelo nome no servidor
        target_channel = utils.get(ctx.guild.text_channels, name=channel_name)
        
        if not target_channel:
            await ctx.respond(
                f"Erro: O canal `#{channel_name}` não foi encontrado."
                f"Execute o `/setup-servidor` primeiro.",
                ephemeral=True
            )
            return
        
        # Se o canal foi encontrado, abre o Modal para o usuário
        modal = CTAModal(bot=self.bot, target_channel_id=target_channel.id, cta_type=tipo)
        await ctx.send_modal(modal)

    @cta.error
    async def cta_error(self, ctx: discord.ApplicationContext, error):
        """Handler de erro específico para o /cta."""
        if isinstance(error, commands.MissingPermissions):
            await ctx.respond("Apenas Oficiais e Líderes podem usar este comando.", ephemeral=True)
        else:
            await ctx.respond(f"Ocorreu um erro inesperado: {error}", ephemeral=True)
            print(f"Erro no comando '/cta': {error}")

# --- 7. Função de Setup (Obrigatória para Cogs) ---
# O main.py (refatorado) chamará esta função automaticamente
async def setup(bot):
    await bot.add_cog(CTACog(bot))