import discord
from discord import app_commands # IMPORTAÇÃO ADICIONADA
from discord.ext import commands
from discord.utils import get
import asyncio

# --- Funções Auxiliares (get_or_create_role, get_or_create_category, etc...) ---
# (Todo o código das funções auxiliares permanece IDÊNTICO ao que já tínhamos)
# ... (O código das 5 funções auxiliares de criação vai aqui) ...
async def get_or_create_role(guild: discord.Guild, name: str, **kwargs):
    existing_role = next((r for r in guild.roles if r.name.lower() == name.lower()), None)
    if existing_role:
        print(f"  [SKIP] Cargo '{name}' já existe.")
        return existing_role
    print(f"  [CREATE] Criando cargo '{name}'...")
    return await guild.create_role(name=name, **kwargs)

async def get_or_create_category(guild: discord.Guild, name: str, **kwargs):
    existing_cat = next((c for c in guild.categories if c.name.lower() == name.lower()), None)
    if existing_cat:
        print(f"  [SKIP] Categoria '{name}' já existe.")
        return existing_cat
    print(f"  [CREATE] Criando Categoria '{name}'...")
    return await guild.create_category(name=name, **kwargs)

async def get_or_create_channel(guild: discord.Guild, name: str, category: discord.CategoryChannel = None, is_text: bool = True, **kwargs):
    search_scope = category.channels if category else guild.channels
    channel_type = discord.ChannelType.text if is_text else discord.ChannelType.voice
    existing_channel = next((c for c in search_scope if c.name.lower() == name.lower() and c.type == channel_type), None)
    if existing_channel:
        print(f"    [SKIP] Canal '{name}' já existe.")
        if 'overwrites' in kwargs:
            await existing_channel.edit(overwrites=kwargs['overwrites'])
            print(f"    [UPDATE] Permissões do canal '{name}' atualizadas.")
        return existing_channel
    print(f"    [CREATE] Criando canal '{name}'...")
    if is_text:
        return await guild.create_text_channel(name=name, category=category, **kwargs)
    else:
        return await guild.create_voice_channel(name=name, category=category, **kwargs)

# --- Funções de Setup (create_roles, setup_publico, etc...) ---
# (Todo o código das 9 funções de setup permanece IDÊNTICO)
# ... (O código das 9 funções de setup vai aqui) ...
async def create_roles(guild):
    print("Iniciando criação de Cargos...")
    r = {
        "everyone": guild.default_role,
        "recruta": await get_or_create_role(guild, name="Recruta", colour=discord.Colour.light_grey()),
        "mercenario": await get_or_create_role(guild, name="Mercenário", colour=discord.Colour.green()),
        "coach": await get_or_create_role(guild, name="Coach", colour=discord.Colour.blue()),
        "shotcaller": await get_or_create_role(guild, name="Shotcaller", colour=discord.Colour.gold()),
        "oficial": await get_or_create_role(guild, name="Oficial", colour=discord.Colour.purple()),
        "lider": await get_or_create_role(guild, name="Líder", colour=discord.Colour.red()),
        "tank": await get_or_create_role(guild, name="Tank", colour=discord.Colour(0x607d8b)),
        "healer": await get_or_create_role(guild, name="Healer", colour=discord.Colour(0x4caf50)),
        "dps": await get_or_create_role(guild, name="DPS", colour=discord.Colour(0xf44336)),
        "suporte": await get_or_create_role(guild, name="Suporte", colour=discord.Colour(0x9c27b0)),
        "lider_tank": await get_or_create_role(guild, name="Líder-Tank"),
        "lider_healer": await get_or_create_role(guild, name="Líder-Healer"),
        "lider_dps": await get_or_create_role(guild, name="Líder-DPS"),
        "lider_suporte": await get_or_create_role(guild, name="Líder-Suporte"),
    }
    print("Criação de Cargos concluída.")
    return r
async def setup_publico(guild, roles):
    """Cria a Categoria PÚBLICO"""
    print("Configurando Categoria: PÚBLICO...")
    cat = await get_or_create_category(guild, "🌎 CATEGORIA: PÚBLICO")
    
    # Canal de Anúncios
    ow_anuncios = { roles["everyone"]: discord.PermissionOverwrite(read_messages=True, send_messages=False) }
    ch_anuncios = await get_or_create_channel(guild, "📢 | anuncios-publicos", cat, overwrites=ow_anuncios)
    # --- LÓGICA ADICIONADA PARA MENSAGEM ---
    if not [msg async for msg in ch_anuncios.history(limit=1)]:
        await ch_anuncios.send(
            "Este é o canal de **Anúncios Públicos**.\n\n"
            "Fique de olho aqui para novidades importantes sobre o *core* que são abertas a todos."
        )
    # -----------------------------------------

    # Canal de Recrutamento
    ow_recrutamento = { roles["everyone"]: discord.PermissionOverwrite(read_messages=True, send_messages=True) } # Permitir /aplicar
    ch_recrutamento = await get_or_create_channel(guild, "✅ | recrutamento", cat, overwrites=ow_recrutamento)
    # --- LÓGICA ADICIONADA PARA MENSAGEM ---
    if not [msg async for msg in ch_recrutamento.history(limit=1)]:
        await ch_recrutamento.send(
            "**Bem-vindo ao Recrutamento!**\n\n"
            "Para se aplicar ao nosso *core*, por favor, use o comando `/aplicar` "
            "(que será configurado no bot) ou aguarde instruções de um Oficial."
        )
    # -----------------------------------------
async def setup_recepcao(guild, roles):
    print("Configurando Categoria: RECEPÇÃO...")
    ow_cat = { roles["everyone"]: discord.PermissionOverwrite(read_messages=False), roles["recruta"]: discord.PermissionOverwrite(read_messages=True), roles["mercenario"]: discord.PermissionOverwrite(read_messages=False), roles["oficial"]: discord.PermissionOverwrite(read_messages=True), }
    cat = await get_or_create_category(guild, "🏁 CATEGORIA: RECEPÇÃO", overwrites=ow_cat)
    ow_ch = { roles["recruta"]: discord.PermissionOverwrite(send_messages=False) }
    await get_or_create_channel(guild, "🚩 | regras-e-diretrizes", cat, overwrites=ow_ch)
    await get_or_create_channel(guild, "👋 | apresente-se", cat)
    await get_or_create_channel(guild, "🤖 | comandos-bot", cat)
async def setup_comunidade(guild, roles):
    print("Configurando Categoria: COMUNIDADE...")
    ow_cat = { roles["everyone"]: discord.PermissionOverwrite(read_messages=False), roles["mercenario"]: discord.PermissionOverwrite(read_messages=True), roles["oficial"]: discord.PermissionOverwrite(read_messages=True), }
    cat = await get_or_create_category(guild, "🌐 CATEGORIA: COMUNIDADE", overwrites=ow_cat)
    ow_ch = { roles["mercenario"]: discord.PermissionOverwrite(send_messages=False) }
    await get_or_create_channel(guild, "📣 | avisos-importantes", cat, overwrites=ow_ch)
    await get_or_create_channel(guild, "💬 | chat-geral", cat)
    await get_or_create_channel(guild, "🎬 | highlights-e-clips", cat)
    await get_or_create_channel(guild, "💰 | loot-e-sorteios", cat)
    await get_or_create_channel(guild, "🎧 Lobby Geral", cat, is_text=False)
async def setup_zvz(guild, roles):
    print("Configurando Categoria: OPERAÇÕES ZVZ...")
    ow_cat = { roles["everyone"]: discord.PermissionOverwrite(read_messages=False), roles["mercenario"]: discord.PermissionOverwrite(read_messages=True), roles["oficial"]: discord.PermissionOverwrite(read_messages=True), }
    cat = await get_or_create_category(guild, "⚔️ CATEGORIA: OPERAÇÕES ZVZ", overwrites=ow_cat)
    ow_ch_cta = { roles["mercenario"]: discord.PermissionOverwrite(send_messages=False) }
    await get_or_create_channel(guild, "❗ | cta-obrigatória", cat, overwrites=ow_ch_cta)
    await get_or_create_channel(guild, "⚔️ | cta-opcional", cat, overwrites=ow_ch_cta)
    await get_or_create_channel(guild, "📅 | registro-cta", cat, overwrites=ow_ch_cta)
    await get_or_create_channel(guild, "📜 | builds-oficiais", cat, overwrites=ow_ch_cta)
    await get_or_create_channel(guild, "🗺️ | estratégia-e-mapa", cat)
    await get_or_create_channel(guild, "🗣️ Concentração ZvZ", cat, is_text=False)
    ow_ch_comando = { roles["everyone"]: discord.PermissionOverwrite(read_messages=True, connect=True), roles["mercenario"]: discord.PermissionOverwrite(speak=False), roles["lider"]: discord.PermissionOverwrite(speak=True, priority_speaker=True), roles["oficial"]: discord.PermissionOverwrite(speak=True, priority_speaker=True), roles["shotcaller"]: discord.PermissionOverwrite(speak=True, priority_speaker=True), roles["lider_tank"]: discord.PermissionOverwrite(speak=True), roles["lider_healer"]: discord.PermissionOverwrite(speak=True), roles["lider_dps"]: discord.PermissionOverwrite(speak=True), roles["lider_suporte"]: discord.PermissionOverwrite(speak=True), }
    await get_or_create_channel(guild, "🎙️ COMANDO (Shotcaller)", cat, is_text=False, overwrites=ow_ch_comando)
async def setup_roles_chat(guild, roles):
    print("Configurando Categoria: COMUNICAÇÃO DE ROLES...")
    ow_cat = { roles["everyone"]: discord.PermissionOverwrite(read_messages=False), roles["mercenario"]: discord.PermissionOverwrite(read_messages=False), roles["oficial"]: discord.PermissionOverwrite(read_messages=True), roles["coach"]: discord.PermissionOverwrite(read_messages=True), }
    cat = await get_or_create_category(guild, "🗣️ CATEGORIA: COMUNICAÇÃO DE ROLES", overwrites=ow_cat)
    await get_or_create_channel(guild, "🛡️ | chat-tanks", cat, overwrites={ roles["tank"]: discord.PermissionOverwrite(read_messages=True) })
    await get_or_create_channel(guild, "💚 | chat-healers", cat, overwrites={ roles["healer"]: discord.PermissionOverwrite(read_messages=True) })
    await get_or_create_channel(guild, "💥 | chat-dps", cat, overwrites={ roles["dps"]: discord.PermissionOverwrite(read_messages=True) })
    await get_or_create_channel(guild, "✨ | chat-suporte", cat, overwrites={ roles["suporte"]: discord.PermissionOverwrite(read_messages=True) })
async def setup_mentoria(guild, roles):
    print("Configurando Categoria: MENTORIA (VODS)...")
    ow_cat = { roles["everyone"]: discord.PermissionOverwrite(read_messages=False), roles["mercenario"]: discord.PermissionOverwrite(read_messages=True), roles["oficial"]: discord.PermissionOverwrite(read_messages=True), }
    cat = await get_or_create_category(guild, "📈 CATEGORIA: MENTORIA (VODS)", overwrites=ow_cat)
    ow_ch_info = { roles["mercenario"]: discord.PermissionOverwrite(send_messages=False) }
    await get_or_create_channel(guild, "ℹ️ | como-gravar-e-postar", cat, overwrites=ow_ch_info)
    ow_ch_feedback = { roles["mercenario"]: discord.PermissionOverwrite(send_messages=False), roles["coach"]: discord.PermissionOverwrite(send_messages=True), roles["oficial"]: discord.PermissionOverwrite(send_messages=True), }
    await get_or_create_channel(guild, "🧑‍🏫 | feedback-dos-coaches", cat, overwrites=ow_ch_feedback)
    await get_or_create_channel(guild, "🛡️ | vods-tank", cat)
    await get_or_create_channel(guild, "💚 | vods-healer", cat)
    await get_or_create_channel(guild, "💥 | vods-dps", cat)
    await get_or_create_channel(guild, "✨ | vods-suporte", cat)
    await get_or_create_channel(guild, "📺 Sala de Análise 1", cat, is_text=False)
    await get_or_create_channel(guild, "📺 Sala de Análise 2", cat, is_text=False)
async def setup_financeiro(guild, roles):
    print("Configurando Categoria: GESTÃO FINANCEIRA...")
    ow_cat = { roles["everyone"]: discord.PermissionOverwrite(read_messages=False), roles["mercenario"]: discord.PermissionOverwrite(read_messages=True), roles["oficial"]: discord.PermissionOverwrite(read_messages=True), }
    cat = await get_or_create_category(guild, "💰 CATEGORIA: GESTÃO FINANCEIRA", overwrites=ow_cat)
    ow_ch_info = { roles["mercenario"]: discord.PermissionOverwrite(send_messages=False) }
    await get_or_create_channel(guild, "ℹ️ | info-regear-e-loot", cat, overwrites=ow_ch_info)
    await get_or_create_channel(guild, "📦 | solicitar-regear", cat)
    ow_ch_logs = { roles["mercenario"]: discord.PermissionOverwrite(send_messages=False) }
    await get_or_create_channel(guild, "🧾 | lootsplit-e-pagamentos", cat, overwrites=ow_ch_logs)
async def setup_admin(guild, roles):
    print("Configurando Categoria: ADMINISTRAÇÃO...")
    ow_cat = { roles["everyone"]: discord.PermissionOverwrite(read_messages=False), roles["mercenario"]: discord.PermissionOverwrite(read_messages=False), roles["oficial"]: discord.PermissionOverwrite(read_messages=True), roles["lider"]: discord.PermissionOverwrite(read_messages=True), }
    cat = await get_or_create_category(guild, "🔒 CATEGORIA: ADMINISTRAÇÃO", overwrites=ow_cat)
    await get_or_create_channel(guild, "💬 | chat-liderança", cat)
    await get_or_create_channel(guild, "📊 | gerenciamento-core", cat)
    await get_or_create_channel(guild, "✅ | regears-aprovados", cat)
    await get_or_create_channel(guild, "🤖 | logs-do-bot", cat)
    await get_or_create_channel(guild, "🔒 Reunião de Oficiais", cat, is_text=False)

# --- A Classe Cog (Módulo) ---

class SetupCog(commands.Cog):
    """Cog que contém todos os comandos relacionados ao setup do servidor."""
    
    def __init__(self, bot):
        self.bot = bot
        print(">>> setup_cog.py FOI LIDO E INICIADO <<<")

    # ----- MUDANÇA CRÍTICA AQUI -----
    @app_commands.command(
        name="setup-servidor",
        description="Configura este servidor do zero de forma segura. (Apenas Admins)"
    )
    @app_commands.checks.has_permissions(administrator=True) # MUDANÇA AQUI
    async def setup_servidor(self, interaction: discord.Interaction): # MUDANÇA AQUI
        """Comando principal que constrói todo o servidor."""
        
        # MUDANÇA AQUI: `interaction.response.send_message`
        await interaction.response.send_message(
            "Comando `/setup-servidor` recebido! Iniciando a configuração segura (Idempotente)...", 
            ephemeral=True
        )
        
        guild = interaction.guild # MUDANÇA AQUI
        
        # MUDANÇA AQUI: `interaction.followup.send`
        main_message = await interaction.followup.send(
            f"Iniciando a configuração completa do servidor '{guild.name}'..."
        )
        
        try:
            # (O resto da lógica do try/except permanece IDÊNTICA)
            await main_message.edit(content="PASSO 1/9: Criando cargos...")
            roles = await create_roles(guild)
            await main_message.edit(content="PASSO 2/9: Configurando Categoria: PÚBLICO...")
            await setup_publico(guild, roles)
            await main_message.edit(content="PASSO 3/9: Configurando Categoria: RECEPÇÃO...")
            await setup_recepcao(guild, roles)
            await main_message.edit(content="PASSO 4/9: Configurando Categoria: COMUNIDADE...")
            await setup_comunidade(guild, roles)
            await main_message.edit(content="PASSO 5/9: Configurando Categoria: OPERAÇÕES ZVZ...")
            await setup_zvz(guild, roles)
            await main_message.edit(content="PASSO 6/9: Configurando Categoria: COMUNICAÇÃO DE ROLES...")
            await setup_roles_chat(guild, roles)
            await main_message.edit(content="PASSO 7/9: Configurando Categoria: MENTORIA (VODS)...")
            await setup_mentoria(guild, roles)
            await main_message.edit(content="PASSO 8/9: Configurando Categoria: GESTÃO FINANCEIRA...")
            await setup_financeiro(guild, roles)
            await main_message.edit(content="PASSO 9/9: Configurando Categoria: ADMINISTRAÇÃO...")
            await setup_admin(guild, roles)
            await main_message.edit(content="🚀 **Configuração do Servidor Concluída!** 🚀\nO servidor está pronto.")

        except discord.Forbidden:
            await main_message.edit(content="**ERRO DE PERMISSÃO:** O Bot não tem permissão para 'Gerir Cargos' ou 'Gerir Canais'.")
        except Exception as e:
            await main_message.edit(content=f"**ERRO INESPERADO:** A configuração falhou.\n`{e}`")
            print(f"Erro no comando '/setup-servidor': {e}")
            import traceback
            traceback.print_exc()

    # O error handler da Cog precisa ser atualizado para lidar com app_commands
    @setup_servidor.error
    async def setup_servidor_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Handler de erro específico para este comando."""
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("Apenas administradores podem usar este comando.", ephemeral=True)
        else:
            # Se a interação já foi respondida, usa followup
            send_func = interaction.followup.send if interaction.response.is_done() else interaction.response.send_message
            await send_func(f"Ocorreu um erro inesperado: {error}", ephemeral=True)
            print(f"Erro no comando '/setup-servidor': {error}")
            import traceback
            traceback.print_exc()

# Função obrigatória que o main.py usa para carregar esta Cog
async def setup(bot):
    await bot.add_cog(SetupCog(bot))