import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import get
import asyncio
import traceback

# --- Nomes das Categorias v2.3 ---
CAT_NAMES = [
    "🌎 PÚBLICO",
    "🏁 RECEPÇÃO (ALIANÇA)",
    "🏛️ ALIANÇA: PACTO SOMBRIO",
    "🏁 RECEPÇÃO (CORE)",
    "⚔️ OPERAÇÕES ZVZ (CORE)",
    "📈 MENTORIA (VODS) (CORE)",
    "💰 GESTÃO FINANCEIRA (CORE)",
    "🗣️ COMUNICAÇÃO DE ROLES (CORE)",
    "🔒 ADMINISTRAÇÃO",
    "🔒 ADMINISTRAÇÃO (CORE E ALIANÇA)", # Nome antigo
    "🌀 DG AVALONIANA"
]

# --- Funções Auxiliares de Criação de Estrutura ---

async def create_role_if_not_exists(guild: discord.Guild, name: str, **kwargs):
    """ Verifica se um cargo existe (case-insensitive). Se não, cria. """
    existing_role = discord.utils.get(guild.roles, name=name)
    if existing_role:
        print(f"  [SKIP] Cargo '{name}' já existe.")
        return existing_role
    print(f"  [CREATE] Criando cargo '{name}'...")
    try:
        return await guild.create_role(name=name, **kwargs)
    except Exception as e:
        print(f"  [ERRO] Falha ao criar cargo '{name}': {e}")
        raise

async def create_category_and_channels(guild: discord.Guild, name: str, channels_to_create: list, overwrites_cat: dict = None):
    """Cria uma categoria e todos os seus canais, enviando mensagens em cada um."""
    print(f"  [CREATE] Criando Categoria '{name}'...")
    try:
        category = await guild.create_category(name=name, overwrites=overwrites_cat or {})
        await asyncio.sleep(0.5)
    except Exception as e:
        print(f"  [ERRO] Falha ao criar categoria '{name}': {e}")
        return None

    print(f"    Criando canais para '{name}'...")
    for channel_info in channels_to_create:
        ch_name = channel_info["name"]
        is_text = channel_info.get("is_text", True)
        overwrites_ch = channel_info.get("overwrites", {})
        initial_message = channel_info.get("message", None)

        print(f"      [CREATE] Criando canal '{ch_name}'...")
        try:
            if is_text:
                channel = await category.create_text_channel(name=ch_name, overwrites=overwrites_ch)
                if initial_message:
                    await asyncio.sleep(0.2)
                    await channel.send(initial_message)
            else: # Canal de Voz
                await category.create_voice_channel(name=ch_name, overwrites=overwrites_ch)
            await asyncio.sleep(0.3)
        except Exception as e:
            print(f"      [ERRO] Falha ao criar/enviar msg no canal '{ch_name}': {e}")

    return category

# --- Definição da Estrutura v2.3 ---

async def create_roles_v2_3(guild: discord.Guild):
    """Cria os cargos da estrutura v2.3 (com DG Avalon)."""
    print("Iniciando criação/verificação de Cargos v2.3...")
    r = {
        "everyone": guild.default_role,
        # Gestão
        "lider_ivexi": await create_role_if_not_exists(guild, name="Líder (IVEXI)", colour=discord.Colour.red(), hoist=True, mentionable=True),
        "lider_pacto": await create_role_if_not_exists(guild, name="Líder (Pacto Sombrio)", colour=discord.Colour.dark_teal(), hoist=True, mentionable=True),
        "oficial_core": await create_role_if_not_exists(guild, name="Oficial (Core IVEXI)", colour=discord.Colour.purple(), hoist=True, mentionable=True),
        # Acesso
        "aliado_pacto": await create_role_if_not_exists(guild, name="Aliado (Pacto Sombrio)", colour=discord.Colour.teal()),
        "core_zvz": await create_role_if_not_exists(guild, name="Core ZvZ (IVEXI)", colour=discord.Colour.green(), hoist=True),
        "recruta_core": await create_role_if_not_exists(guild, name="Recruta (Core)", colour=discord.Colour.light_grey()),
        
        # ----- MUDANÇA CRÍTICA AQUI -----
        "dg_avaloniana": await create_role_if_not_exists(guild, name="DG Avaloniana", colour=discord.Colour.magenta(), hoist=True), # Cor corrigida de .nitro_pink() para .magenta()
        # ---------------------------------
        
        # Funcionais (Core)
        "tank": await create_role_if_not_exists(guild, name="Tank", colour=discord.Colour(0x607d8b)),
        "healer": await create_role_if_not_exists(guild, name="Healer", colour=discord.Colour(0x4caf50)),
        "dps": await create_role_if_not_exists(guild, name="DPS", colour=discord.Colour(0xf44336)),
        "suporte": await create_role_if_not_exists(guild, name="Suporte", colour=discord.Colour(0x9c27b0)),
        "coach": await create_role_if_not_exists(guild, name="Coach", colour=discord.Colour.blue()),
        "shotcaller": await create_role_if_not_exists(guild, name="Shotcaller", colour=discord.Colour.gold()),
        "lider_tank": await create_role_if_not_exists(guild, name="Líder-Tank"),
        "lider_healer": await create_role_if_not_exists(guild, name="Líder-Healer"),
        "lider_dps": await create_role_if_not_exists(guild, name="Líder-DPS"),
        "lider_suporte": await create_role_if_not_exists(guild, name="Líder-Suporte"),
    }
    print("Criação/Verificação de Cargos v2.3 concluída.")
    return r

def get_channel_definitions_v2_3(roles: dict):
    """Retorna o dicionário completo da estrutura de canais v2.3."""

    # --- Permissões Base ---
    ow_publico = { roles["everyone"]: discord.PermissionOverwrite(read_messages=True) }
    
    ow_alianca = {
        roles["everyone"]: discord.PermissionOverwrite(read_messages=False),
        roles["aliado_pacto"]: discord.PermissionOverwrite(read_messages=True),
        roles["recruta_core"]: discord.PermissionOverwrite(read_messages=True),
        roles["core_zvz"]: discord.PermissionOverwrite(read_messages=True),
        roles["dg_avaloniana"]: discord.PermissionOverwrite(read_messages=True),
        roles["oficial_core"]: discord.PermissionOverwrite(read_messages=True),
        roles["lider_pacto"]: discord.PermissionOverwrite(read_messages=True),
        roles["lider_ivexi"]: discord.PermissionOverwrite(read_messages=True),
    }
    
    ow_recepcao_core = {
        roles["everyone"]: discord.PermissionOverwrite(read_messages=False),
        roles["aliado_pacto"]: discord.PermissionOverwrite(read_messages=False),
        roles["dg_avaloniana"]: discord.PermissionOverwrite(read_messages=False),
        roles["recruta_core"]: discord.PermissionOverwrite(read_messages=True),
        roles["core_zvz"]: discord.PermissionOverwrite(read_messages=False),
        roles["oficial_core"]: discord.PermissionOverwrite(read_messages=True),
        roles["lider_ivexi"]: discord.PermissionOverwrite(read_messages=True),
    }
    
    ow_operacoes_core = {
        roles["everyone"]: discord.PermissionOverwrite(read_messages=False),
        roles["aliado_pacto"]: discord.PermissionOverwrite(read_messages=True, connect=True),
        roles["recruta_core"]: discord.PermissionOverwrite(read_messages=True, connect=True),
        roles["core_zvz"]: discord.PermissionOverwrite(read_messages=True, connect=True),
        roles["dg_avaloniana"]: discord.PermissionOverwrite(read_messages=False),
        roles["oficial_core"]: discord.PermissionOverwrite(read_messages=True),
        roles["lider_ivexi"]: discord.PermissionOverwrite(read_messages=True),
    }

    ow_core_privado = {
        roles["everyone"]: discord.PermissionOverwrite(read_messages=False),
        roles["aliado_pacto"]: discord.PermissionOverwrite(read_messages=False),
        roles["recruta_core"]: discord.PermissionOverwrite(read_messages=False), 
        roles["dg_avaloniana"]: discord.PermissionOverwrite(read_messages=False),
        roles["core_zvz"]: discord.PermissionOverwrite(read_messages=True),
        roles["oficial_core"]: discord.PermissionOverwrite(read_messages=True),
        roles["lider_ivexi"]: discord.PermissionOverwrite(read_messages=True),
    }
    
    ow_roles_privado = {
        **ow_core_privado,
        roles["core_zvz"]: discord.PermissionOverwrite(read_messages=False),
        roles["coach"]: discord.PermissionOverwrite(read_messages=True),
    }
    
    ow_dg_avaloniana = {
        roles["everyone"]: discord.PermissionOverwrite(read_messages=False),
        roles["aliado_pacto"]: discord.PermissionOverwrite(read_messages=False),
        roles["recruta_core"]: discord.PermissionOverwrite(read_messages=False),
        roles["core_zvz"]: discord.PermissionOverwrite(read_messages=False),
        roles["dg_avaloniana"]: discord.PermissionOverwrite(read_messages=True),
        roles["oficial_core"]: discord.PermissionOverwrite(read_messages=True),
        roles["lider_ivexi"]: discord.PermissionOverwrite(read_messages=True),
    }

    ow_admin = {
        roles["everyone"]: discord.PermissionOverwrite(read_messages=False),
        roles["aliado_pacto"]: discord.PermissionOverwrite(read_messages=False),
        roles["recruta_core"]: discord.PermissionOverwrite(read_messages=False),
        roles["core_zvz"]: discord.PermissionOverwrite(read_messages=False),
        roles["dg_avaloniana"]: discord.PermissionOverwrite(read_messages=False),
        roles["oficial_core"]: discord.PermissionOverwrite(read_messages=True),
        roles["lider_pacto"]: discord.PermissionOverwrite(read_messages=True),
        roles["lider_ivexi"]: discord.PermissionOverwrite(read_messages=True),
    }

    # --- Definições de Canais v2.3 ---
    return {
        "🌎 PÚBLICO": {
            "overwrites": ow_publico,
            "channels": [
                {"name": "🚩 | regras-e-diplomacia", "overwrites": {roles["everyone"]: discord.PermissionOverwrite(send_messages=False)},
                 "message": "Bem-vindo ao **QG da Aliança Pacto Sombrio**, liderada pela **IVEXI**.\n\n**Diplomacia:**\nLíderes de outras guildas, por favor, contactem um @Líder (IVEXI) ou @Líder (Pacto Sombrio)."},
                {"name": "✅ | recrutamento-alianca", "overwrites": {roles["everyone"]: discord.PermissionOverwrite(send_messages=True, read_messages=True)},
                 "message": "**Recrutamento Aberto - Pacto Sombrio**\n\nGuildas ou jogadores interessados em juntar-se à aliança, iniciem a conversa aqui."},
                {"name": "📢 | avisos", "overwrites": {roles["everyone"]: discord.PermissionOverwrite(send_messages=False)}},
                {"name": "💬 | geral", "is_text": True},
                {"name": "📞 | Geral (Voz)", "is_text": False},
            ]
        },
        "🏁 RECEPÇÃO (ALIANÇA)": {
            "overwrites": ow_alianca,
            "channels": [
                {"name": "👋 | bem-vindo-alianca", "overwrites": {roles["everyone"]: discord.PermissionOverwrite(send_messages=False)},
                 "message": "Membros de guildas aliadas, bem-vindos! Apresentem-se e aguardem um oficial para receberem seus cargos."},
            ]
        },
        "🏛️ ALIANÇA: PACTO SOMBRIO": {
            "overwrites": ow_alianca,
            "channels": [
                {"name": "📢 | avisos-alianca", "overwrites": {**ow_alianca, roles["aliado_pacto"]: discord.PermissionOverwrite(read_messages=True, send_messages=False)}},
                {"name": "💬 | geral-alianca", "is_text": True},
                {"name": "📞 | Aliança (Voz)", "is_text": False},
            ]
        },
        "🏁 RECEPÇÃO (CORE)": {
            "overwrites": ow_recepcao_core,
            "channels": [
                {"name": "👋 | bem-vindo-core", "message": "Recrutas, leiam as informações e sigam os próximos passos para se juntarem ao Core ZvZ."},
                {"name": "📜 | regras-core", "overwrites": {**ow_recepcao_core, roles["recruta_core"]: discord.PermissionOverwrite(read_messages=True, send_messages=False)}},
            ]
        },
        "⚔️ OPERAÇÕES ZVZ (CORE)": {
            "overwrites": ow_operacoes_core,
            "channels": [
                {"name": "❗ | cta-obrigatória", "overwrites": {**ow_operacoes_core, roles["core_zvz"]: discord.PermissionOverwrite(read_messages=True, send_messages=False)}},
                {"name": "⚔️ | cta-opcional", "overwrites": {**ow_operacoes_core, roles["core_zvz"]: discord.PermissionOverwrite(read_messages=True, send_messages=False)}},
                {"name": "📣 | Calls ZvZ", "is_text": False},
                {"name": "💬 | Chat ZvZ", "is_text": True},
            ]
        },
        "📈 MENTORIA (VODS) (CORE)": {
            "overwrites": ow_core_privado,
            "channels": [
                {"name": "📚 | vods-e-análises", "is_text": True},
                {"name": "📞 | Análise de VODs (Voz)", "is_text": False},
            ]
        },
        "💰 GESTÃO FINANCEIRA (CORE)": {
            "overwrites": ow_core_privado,
            "channels": [
                {"name": "📦 | loot-regear", "is_text": True},
            ]
        },
        "🗣️ COMUNICAÇÃO DE ROLES (CORE)": {
            "overwrites": ow_roles_privado,
            "channels": [
                {"name": "🛡️ | tanks", "is_text": True},
                {"name": "💚 | healers", "is_text": True},
                {"name": "딜 | dps", "is_text": True},
                {"name": "✨ | suportes", "is_text": True},
                {"name": "🎓 | coaches", "is_text": True},
            ]
        },
        "🌀 DG AVALONIANA": {
            "overwrites": ow_dg_avaloniana,
            "channels": [
                {"name": "💬 | chat-ava-dg", "is_text": True},
                {"name": "📞 | Grupo DG (Voz)", "is_text": False},
            ]
        },
        "🔒 ADMINISTRAÇÃO": {
            "overwrites": ow_admin,
            "channels": [
                {"name": "🔒 | chat-oficiais", "is_text": True},
                {"name": "📞 | Reunião (Voz)", "is_text": False},
                {"name": "🤖 | logs-bot", "is_text": True},
            ]
        }
    }

# --- Definição da Cog ---

class SetupCog(commands.Cog):
    """Módulo com comandos para configurar o servidor (apenas admins)."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print(">>> setup_cog.py FOI LIDO E INICIADO <<<")

    @app_commands.command(name="setup-servidor", description="[ADMIN] Cria todos os cargos e canais necessários para o servidor.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_servidor(self, interaction: discord.Interaction):
        """Executa a rotina completa de setup do servidor."""
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("Este comando só pode ser usado em um servidor.", ephemeral=True)
            return

        await interaction.response.send_message("**Iniciando configuração do servidor...**\nIsso pode levar alguns minutos. Verifique o console para detalhes.", ephemeral=True)
        print(f"\n--- INICIANDO SETUP PARA O SERVIDOR: {guild.name} ---")

        try:
            roles = await create_roles_v2_3(guild)
            channel_definitions = get_channel_definitions_v2_3(roles)

            for cat_name, cat_data in channel_definitions.items():
                await create_category_and_channels(guild, cat_name, cat_data["channels"], cat_data.get("overwrites"))

            await interaction.followup.send("✅ **Configuração do servidor concluída com sucesso!**", ephemeral=True)
            print(f"--- SETUP CONCLUÍDO PARA: {guild.name} ---\n")

        except Exception as e:
            error_message = f"Ocorreu um erro crítico durante o setup: {e}"
            traceback_str = traceback.format_exc()
            print(f"[ERRO CRÍTICO] {error_message}\n{traceback_str}")
            await interaction.followup.send(f"❌ **Falha no Setup!**\n{error_message}\nVerifique o console para o traceback completo.", ephemeral=True)

    @setup_servidor.error
    async def setup_servidor_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("Apenas administradores do servidor podem usar este comando.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Ocorreu um erro inesperado: {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SetupCog(bot))