import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import get
import asyncio
import traceback

# --- Nomes das Categorias v2.2 ---
# Esta lista é usada para a limpeza.
CAT_NAMES = [
    "🌎 PÚBLICO",
    "🏁 RECEPÇÃO (ALIANÇA)",
    "🏛️ ALIANÇA: PACTO SOMBRIO",
    "🏁 RECEPÇÃO (CORE)",
    "⚔️ OPERAÇÕES ZVZ (CORE)",
    "📈 MENTORIA (VODS) (CORE)",
    "💰 GESTÃO FINANCEIRA (CORE)",
    "🗣️ COMUNICAÇÃO DE ROLES (CORE)",
    "🔒 ADMINISTRAÇÃO"
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
        # Aplica permissões de categoria base
        category = await guild.create_category(name=name, overwrites=overwrites_cat or {})
        await asyncio.sleep(0.5)
    except Exception as e:
        print(f"  [ERRO] Falha ao criar categoria '{name}': {e}")
        return None # Aborta esta categoria se a criação falhar

    print(f"    Criando canais para '{name}'...")
    for channel_info in channels_to_create:
        ch_name = channel_info["name"]
        is_text = channel_info.get("is_text", True)
        # Permissões do canal são ADICIONADAS às da categoria
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
            # Continua para os próximos canais

    return category

# --- Definição da Estrutura v2.2 ---

async def create_roles_v2(guild: discord.Guild):
    """Cria os cargos da estrutura v2.2."""
    print("Iniciando criação/verificação de Cargos v2.2...")
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
    print("Criação/Verificação de Cargos v2.2 concluída.")
    return r

def get_channel_definitions_v2(roles: dict):
    """Retorna o dicionário completo da estrutura de canais v2.2."""

    # --- Permissões Base ---
    # Permissão para Categoria PÚBLICO
    ow_publico = {
        roles["everyone"]: discord.PermissionOverwrite(read_messages=True)
    }
    # Permissão para Categorias ALIANÇA
    ow_alianca = {
        roles["everyone"]: discord.PermissionOverwrite(read_messages=False),
        roles["aliado_pacto"]: discord.PermissionOverwrite(read_messages=True),
        roles["recruta_core"]: discord.PermissionOverwrite(read_messages=True),
        roles["core_zvz"]: discord.PermissionOverwrite(read_messages=True),
        roles["oficial_core"]: discord.PermissionOverwrite(read_messages=True),
        roles["lider_pacto"]: discord.PermissionOverwrite(read_messages=True),
        roles["lider_ivexi"]: discord.PermissionOverwrite(read_messages=True),
    }
    # Permissão para Categoria RECEPÇÃO (CORE)
    ow_recepcao_core = {
        roles["everyone"]: discord.PermissionOverwrite(read_messages=False),
        roles["aliado_pacto"]: discord.PermissionOverwrite(read_messages=False),
        roles["recruta_core"]: discord.PermissionOverwrite(read_messages=True),
        roles["core_zvz"]: discord.PermissionOverwrite(read_messages=False), # Core aprovado não vê mais
        roles["oficial_core"]: discord.PermissionOverwrite(read_messages=True),
        roles["lider_ivexi"]: discord.PermissionOverwrite(read_messages=True),
    }
    # Permissão para Categorias OPERAÇÕES, MENTORIA, FINANÇAS (CORE)
    ow_core_restrito = {
        roles["everyone"]: discord.PermissionOverwrite(read_messages=False),
        roles["aliado_pacto"]: discord.PermissionOverwrite(read_messages=False),
        roles["recruta_core"]: discord.PermissionOverwrite(read_messages=False), # Recruta NÃO VÊ
        roles["core_zvz"]: discord.PermissionOverwrite(read_messages=True),
        roles["oficial_core"]: discord.PermissionOverwrite(read_messages=True),
        roles["lider_ivexi"]: discord.PermissionOverwrite(read_messages=True),
    }
    # Permissão para Categoria COMUNICAÇÃO DE ROLES (CORE)
    ow_roles_core = {
        roles["everyone"]: discord.PermissionOverwrite(read_messages=False),
        roles["aliado_pacto"]: discord.PermissionOverwrite(read_messages=False),
        roles["recruta_core"]: discord.PermissionOverwrite(read_messages=False),
        roles["core_zvz"]: discord.PermissionOverwrite(read_messages=False), # Vê apenas o seu canal
        roles["oficial_core"]: discord.PermissionOverwrite(read_messages=True),
        roles["coach"]: discord.PermissionOverwrite(read_messages=True),
        roles["lider_ivexi"]: discord.PermissionOverwrite(read_messages=True),
    }
    # Permissão para Categoria ADMINISTRAÇÃO
    ow_admin = {
        roles["everyone"]: discord.PermissionOverwrite(read_messages=False),
        roles["aliado_pacto"]: discord.PermissionOverwrite(read_messages=False),
        roles["recruta_core"]: discord.PermissionOverwrite(read_messages=False),
        roles["core_zvz"]: discord.PermissionOverwrite(read_messages=False),
        roles["oficial_core"]: discord.PermissionOverwrite(read_messages=True),
        roles["lider_pacto"]: discord.PermissionOverwrite(read_messages=True),
        roles["lider_ivexi"]: discord.PermissionOverwrite(read_messages=True),
    }

    # --- Definições de Canais ---
    return {
        "🌎 PÚBLICO": {
            "overwrites": ow_publico,
            "channels": [
                {"name": "🚩 | regras-e-diplomacia", "overwrites": {roles["everyone"]: discord.PermissionOverwrite(send_messages=False)},
                 "message": "Bem-vindo ao **QG da Aliança Pacto Sombrio**, liderada pela **IVEXI**.\n\nEste servidor é focado em performance, coordenação de aliança e operações ZvZ de alto nível.\n\n**Diplomacia:**\nLíderes de outras guildas, por favor, contactem um @Líder (IVEXI) ou @Líder (Pacto Sombrio)."},
                {"name": "✅ | recrutamento-alianca", "overwrites": {roles["everyone"]: discord.PermissionOverwrite(send_messages=True)},
                 "message": "**Recrutamento Aberto - Pacto Sombrio**\n\nGuildas ou jogadores interessados em juntar-se à aliança, iniciem a conversa aqui.\n\nSe procura a guilda **IVEXI**, será redirecionado."},
                {"name": "✅ | aplicar-core-ivexi", "overwrites": {roles["everyone"]: discord.PermissionOverwrite(send_messages=True)},
                 "message": "**Aplicação para o Core ZvZ da IVEXI**\n\nEste canal é para membros **já existentes** da aliança que desejam entrar para a equipa de elite ZvZ.\n\nUse o comando `/aplicar` (funcionalidade futura) para submeter a sua aplicação."}
            ]
        },
        "🏁 RECEPÇÃO (ALIANÇA)": {
            "overwrites": ow_alianca,
            "channels": [
                {"name": "👋 | apresente-se",
                 "message": "Bem-vindo ao QG, Aliado!\n\nUse este canal para se apresentar. Diga-nos o seu Nick, a sua Guilda, e as suas classes principais."},
                {"name": "📢 | anuncios-alianca", "overwrites": {roles["aliado_pacto"]: discord.PermissionOverwrite(send_messages=False)},
                 "message": "Canal de anúncios globais para todas as guildas da aliança **Pacto Sombrio**.\n(Apenas Líderes e Oficiais podem postar aqui)."},
                {"name": "📜 | builds-alianca", "overwrites": {roles["aliado_pacto"]: discord.PermissionOverwrite(send_messages=False)},
                 "message": "Aqui estarão as builds padrão recomendadas para atividades em conjunto da aliança (defesas, roaming, etc.)."},
                {"name": "🤖 | comandos-bot-alianca",
                 "message": "Use este canal para comandos de bot (ex: verificar builds, status, etc.)."}
            ]
        },
        "🏛️ ALIANÇA: PACTO SOMBRIO": {
            "overwrites": ow_alianca,
            "channels": [
                {"name": "💬 | chat-geral-alianca",
                 "message": "Este é o canal social principal da aliança. Sinta-se em casa!"},
                {"name": " pve-grupais",
                 "message": "Organização de Dungeons (Estáticas, Grupo, Avalonianas), Fama Farm, etc."},
                {"name": " small-scale-pvp",
                 "message": "Organização de Ganking, Roaming, Defesa de Hideouts, Castelos, etc."},
                {"name": "💰 | loot-e-sorteios-alianca",
                 "message": "Poste aqui os seus *prints* de *loot* incrível e participe em sorteios da aliança!"},
                {"name": " call-geral-1", "is_text": False},
                {"name": " call-geral-2", "is_text": False},
                {"name": " afk", "is_text": False}
            ]
        },
        "🏁 RECEPÇÃO (CORE)": {
            "overwrites": ow_recepcao_core,
            "channels": [
                {"name": "🚩 | diretrizes-do-core", "overwrites": {roles["recruta_core"]: discord.PermissionOverwrite(send_messages=False)},
                 "message": "Bem-vindo ao processo seletivo do Core ZvZ da IVEXI.\n\n**LEITURA OBRIGATÓRIA (REGRAS DO CORE):**\n\n1. **Mentalidade:** Foco em performance, aceitar críticas e melhorar continuamente.\n2. **Comparecimento:** CTAs obrigatórias são prioridade.\n3. **VODs:** Gravação das suas lutas é 100% obrigatória para análise.\n4. **Builds:** Seguir as builds oficiais do Core é mandatório.\n5. **Comunicação:** Limpa e objetiva durante as lutas."},
                {"name": "👋 | apresente-se-core",
                 "message": "Recruta, use este canal para se apresentar à liderança do Core.\n\nNick, Classe(s) ZvZ, Experiência prévia, Link do seu melhor VOD."}
            ]
        },
        "⚔️ OPERAÇÕES ZVZ (CORE)": {
            "overwrites": ow_core_restrito,
            "channels": [
                {"name": "❗ | cta-obrigatória", "overwrites": {roles["core_zvz"]: discord.PermissionOverwrite(send_messages=False)},
                 "message": "Canal para **CTAs Obrigatórias** (Territórios, Castelos, etc.).\nO bot postará as chamadas aqui. Reaja com ✅, ❌ ou ❓."},
                {"name": "⚔️ | cta-opcional", "overwrites": {roles["core_zvz"]: discord.PermissionOverwrite(send_messages=False)},
                 "message": "Canal para **CTAs Opcionais** (Conteúdo ZvZ secundário, Brawls, etc.)."},
                {"name": "📅 | registro-cta", "overwrites": {roles["core_zvz"]: discord.PermissionOverwrite(send_messages=False)},
                 "message": "Este canal é um **log automático** do bot.\nEle mostrará a lista de quem confirmou presença."},
                {"name": "📜 | builds-oficiais-core", "overwrites": {roles["core_zvz"]: discord.PermissionOverwrite(send_messages=False)},
                 "message": "Aqui estarão fixadas as **Builds Oficiais** do *core*.\nUsar a *build* correta é obrigatório."},
                {"name": "🗺️ | estratégia-e-mapa-core"},
                {"name": "🗣️ Concentração ZvZ (Core)", "is_text": False},
                {"name": "🎙️ COMANDO (Core)", "is_text": False, "overwrites": {
                    roles["core_zvz"]: discord.PermissionOverwrite(speak=False), # Membros do Core não falam
                    roles["lider_ivexi"]: discord.PermissionOverwrite(speak=True, priority_speaker=True),
                    roles["oficial_core"]: discord.PermissionOverwrite(speak=True, priority_speaker=True),
                    roles["shotcaller"]: discord.PermissionOverwrite(speak=True, priority_speaker=True),
                    roles["lider_tank"]: discord.PermissionOverwrite(speak=True), 
                    roles["lider_healer"]: discord.PermissionOverwrite(speak=True),
                    roles["lider_dps"]: discord.PermissionOverwrite(speak=True),
                    roles["lider_suporte"]: discord.PermissionOverwrite(speak=True),
                }}
            ]
        },
        "📈 MENTORIA (VODS) (CORE)": {
            "overwrites": ow_core_restrito,
            "channels": [
                {"name": "ℹ️ | como-gravar-e-postar", "overwrites": {roles["core_zvz"]: discord.PermissionOverwrite(send_messages=False)},
                 "message": "**Tutorial de Gravação (VODs)**\n\nÉ obrigatório gravar suas ZvZs.\n1. **Software:** OBS Studio, ShadowPlay, etc.\n2. **Upload:** YouTube (Não Listado).\n3. **Postagem:** Cole o link no canal da sua *role* (ex: `#🛡️ | vods-tank`)."},
                {"name": "🧑‍🏫 | feedback-dos-coaches", "overwrites": {roles["core_zvz"]: discord.PermissionOverwrite(send_messages=False), roles["coach"]: discord.PermissionOverwrite(send_messages=True), roles["oficial_core"]: discord.PermissionOverwrite(send_messages=True)},
                 "message": "Canal para os **Coaches e Líderes** darem *feedback* geral.\n(Apenas Coaches/Oficiais podem escrever aqui)."},
                {"name": "🛡️ | vods-tank"}, {"name": "💚 | vods-healer"},
                {"name": "💥 | vods-dps"}, {"name": "✨ | vods-suporte"},
                {"name": "📺 Sala de Análise (Core)", "is_text": False}
            ]
        },
        "💰 GESTÃO FINANCEIRA (CORE)": {
            "overwrites": ow_core_restrito,
            "channels": [
                {"name": "ℹ️ | info-regear-e-loot", "overwrites": {roles["core_zvz"]: discord.PermissionOverwrite(send_messages=False)},
                 "message": "**Regras de Regear e Loot Split (CORE)**\n\n**Regear:**\n1. Cobertura em CTAs **obrigatórias**.\n2. Solicite com `/regear` em `#📦 | solicitar-regear`.\n\n**Loot Split:**\n1. Todo *loot* ZvZ é recolhido.\n2. Taxa de X% retida.\n3. Restante dividido entre presentes."},
                {"name": "📦 | solicitar-regear",
                 "message": "Use este canal **apenas** para usar o comando `/regear` e anexar o *screenshot* da sua morte.\nAguarde a reação ✅ ou ❌ de um Oficial."},
                {"name": "🧾 | lootsplit-e-pagamentos", "overwrites": {roles["core_zvz"]: discord.PermissionOverwrite(send_messages=False)},
                 "message": "Canal para a liderança postar os relatórios de **Loot Split** e confirmar pagamentos."}
            ]
        },
        "🗣️ COMUNICAÇÃO DE ROLES (CORE)": {
            "overwrites": ow_roles_core,
            "channels": [
                {"name": "🛡️ | chat-tanks", "overwrites": { roles.get("tank"): discord.PermissionOverwrite(read_messages=True) }},
                {"name": "💚 | chat-healers", "overwrites": { roles.get("healer"): discord.PermissionOverwrite(read_messages=True) }},
                {"name": "💥 | chat-dps", "overwrites": { roles.get("dps"): discord.PermissionOverwrite(read_messages=True) }},
                {"name": "✨ | chat-suporte", "overwrites": { roles.get("suporte"): discord.PermissionOverwrite(read_messages=True) }}
            ]
        },
        "🔒 ADMINISTRAÇÃO": {
            "overwrites": ow_admin,
            "channels": [
                {"name": "💬 | chat-liderança", "message": "Chat privado para líderes do Core IVEXI e da Aliança Pacto Sombrio."},
                {"name": "📊 | gerenciamento-core", "message": "Canal para discutir promoções, recrutamentos e gestão interna do Core ZvZ."},
                {"name": "✅ | regears-aprovados", "message": "Log automático de regears aprovados (funcionalidade futura)."},
                {"name": "🤖 | logs-do-bot", "message": "Canal para o bot reportar erros e logs importantes."},
                {"name": "🔒 Reunião de Oficiais", "is_text": False}
            ]
        }
    }


# --- A Classe Cog (Módulo) ---

class SetupCog(commands.Cog):
    """Cog que contém todos os comandos relacionados ao setup do servidor."""

    def __init__(self, bot):
        self.bot = bot
        print(">>> setup_cog.py (v2.2 - QG Aliança) FOI LIDO E INICIADO <<<")

    async def delete_existing_structure(self, guild: discord.Guild, message_to_edit: discord.Message):
        """Apaga as categorias (e seus canais) gerenciadas pelo bot."""
        await message_to_edit.edit(content="PASSO 0/10: Apagando estrutura antiga (categorias e canais)...")
        print("Iniciando limpeza da estrutura antiga (v2.2)...")
        deleted_count = 0
        
        # Procura categorias pelos nomes exatos da v2.2
        categories_to_delete = [cat for cat in guild.categories if cat.name in CAT_NAMES]

        for category in categories_to_delete:
            print(f"  Apagando categoria '{category.name}' e seus canais...")
            try:
                channels_in_category = list(category.channels)
                for channel in channels_in_category:
                    try:
                        await channel.delete(reason="Recriação da estrutura (v2.2)")
                        deleted_count += 1
                        print(f"    Canal '{channel.name}' apagado.")
                        await asyncio.sleep(0.5)
                    except Exception as e:
                        print(f"    [ERRO] Falha ao apagar canal '{channel.name}': {e}")
                
                await category.delete(reason="Recriação da estrutura (v2.2)")
                deleted_count += 1
                print(f"  Categoria '{category.name}' apagada.")
                await asyncio.sleep(0.5)
            except discord.Forbidden:
                 print(f"  [ERRO DE PERMISSÃO] Não foi possível apagar a categoria '{category.name}'.")
                 await message_to_edit.edit(content=f"**ERRO DE PERMISSÃO:** Não foi possível apagar a categoria '{category.name}'. Verifique as permissões do bot e tente novamente.")
                 raise # Interrompe o setup
            except Exception as e:
                print(f"  [ERRO] Falha ao apagar categoria '{category.name}': {e}")
        
        await message_to_edit.edit(content=f"PASSO 0/10: Limpeza concluída ({deleted_count} itens removidos).")
        print("Limpeza da estrutura antiga concluída.")


    @app_commands.command( name="setup-servidor", description="APAGA e RECria a estrutura do QG da Aliança e Core. (Apenas Admins)")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_servidor(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "⚠️ **AVISO (v2.2):** Este comando irá **APAGAR** as categorias do QG da Aliança e do Core e recriá-las do zero!\n"
            "Confirme digitando `SIM APAGAR TUDO` no chat em 30 segundos.",
            ephemeral=True
        )

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel and m.content == "SIM APAGAR TUDO"

        try:
            confirmation_msg = await self.bot.wait_for('message', timeout=30.0, check=check)
            try: await confirmation_msg.delete()
            except: pass
        except asyncio.TimeoutError:
            await interaction.followup.send("Comando cancelado.", ephemeral=True)
            return
        except Exception as e:
             await interaction.followup.send(f"Erro na confirmação: {e}", ephemeral=True)
             return

        # ---- INÍCIO DA EXECUÇÃO REAL ----
        guild = interaction.guild
        main_message = await interaction.followup.send(f"🔥 Confirmado! Iniciando a recriação da Estrutura v2.2 (QG Pacto Sombrio)...")

        try:
            # PASSO 0: Apagar Estrutura Antiga
            await self.delete_existing_structure(guild, main_message)

            # PASSO 1: Criar Cargos
            await main_message.edit(content="PASSO 1/10: Verificando/Criando cargos v2.2...")
            roles = await create_roles_v2(guild)

            # PASSO 2 a 10: Recriar Categorias e Canais
            
            # Obtém todas as definições de canais
            all_definitions = get_channel_definitions_v2(roles)

            # Lista ordenada de categorias para criação
            # Os nomes DEVEM corresponder às chaves em `all_definitions` e `CAT_NAMES`
            categorias_para_criar = [
                "🌎 PÚBLICO",
                "🏁 RECEPÇÃO (ALIANÇA)",
                "🏛️ ALIANÇA: PACTO SOMBRIO",
                "🏁 RECEPÇÃO (CORE)",
                "⚔️ OPERAÇÕES ZVZ (CORE)",
                "📈 MENTORIA (VODS) (CORE)",
                "💰 GESTÃO FINANCEIRA (CORE)",
                "🗣️ COMUNICAÇÃO DE ROLES (CORE)",
                "🔒 ADMINISTRAÇÃO"
            ]

            for i, cat_name in enumerate(categorias_para_criar):
                 step_num = i + 2 # Começa no passo 2
                 await main_message.edit(content=f"PASSO {step_num}/10: Recriando Categoria: {cat_name}...")
                 
                 definition = all_definitions.get(cat_name)
                 if not definition:
                     print(f"  [AVISO] Nenhuma definição de canal encontrada para '{cat_name}'. Pulando.")
                     continue
                 
                 channels_list = definition.get("channels", [])
                 cat_overwrites = definition.get("overwrites", {})
                 
                 await create_category_and_channels(guild, cat_name, channels_list, cat_overwrites)
                 await asyncio.sleep(0.5)

            await main_message.edit(content="🚀 **Recriação Completa (v2.2) do QG Concluída!** 🚀")

        except discord.Forbidden as e:
            await main_message.edit(content=f"**ERRO DE PERMISSÃO DURANTE A CRIAÇÃO:** {e}. Verifique as permissões do bot.")
            traceback.print_exc()
        except Exception as e:
            await main_message.edit(content=f"**ERRO INESPERADO DURANTE A CRIAÇÃO:** {type(e).__name__}: {e}. Verifique os logs.")
            print(f"Erro detalhado no comando '/setup-servidor':")
            traceback.print_exc()

    @setup_servidor.error
    async def setup_servidor_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
             if not interaction.response.is_done(): await interaction.response.send_message("Apenas administradores podem usar este comando.", ephemeral=True)
             else: await interaction.followup.send("Apenas administradores podem usar este comando.", ephemeral=True)
        else:
            send_func = interaction.followup.send if interaction.response.is_done() else interaction.response.send_message
            try:
                await send_func(f"Erro (handler): {type(error).__name__}", ephemeral=True)
            except discord.NotFound: print("Erro no setup_servidor_error: Interação expirou.")
            except Exception as e: print(f"Erro ao enviar msg de erro no handler: {e}")
            print(f"Erro não tratado no comando '/setup-servidor':")
            traceback.print_exc()

async def setup(bot):
    await bot.add_cog(SetupCog(bot))