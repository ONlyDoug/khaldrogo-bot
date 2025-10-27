# cogs/setup_cog.py
import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import get
import asyncio
import traceback

# --- Funções Auxiliares de Criação ---

async def get_or_create_role(guild: discord.Guild, name: str, **kwargs):
    """ Tenta encontrar um cargo pelo nome (case-insensitive). Se não existir, cria-o. """
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

async def get_or_create_category(guild: discord.Guild, name: str, **kwargs):
    """ Tenta encontrar uma categoria pelo nome (case-insensitive). Se não existir, cria-a. """
    existing_cat = discord.utils.get(guild.categories, name=name)
    if existing_cat:
        print(f"  [SKIP] Categoria '{name}' já existe (será apagada).")
    print(f"  [CREATE] Preparando para criar Categoria '{name}'...")
    return None # Criação será feita após a limpeza

async def create_category_and_channels(guild: discord.Guild, name: str, channels_to_create: list, roles: dict, overwrites_cat: dict = None):
    """Cria uma categoria e seus canais associados."""
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
                    # Verifica se o canal está realmente vazio (evita spam em caso de erro anterior)
                    is_empty = not [msg async for msg in channel.history(limit=1)]
                    if is_empty:
                        await channel.send(initial_message)
            else: # Canal de Voz
                await category.create_voice_channel(name=ch_name, overwrites=overwrites_ch)
            await asyncio.sleep(0.3)
        except Exception as e:
            print(f"      [ERRO] Falha ao criar/enviar msg no canal '{ch_name}': {e}")
            # Continua para os próximos canais

    return category

# --- Nomes das Categorias ---
CAT_NAMES = [
    "🌎 PÚBLICO", "🏁 RECEPÇÃO", "🌐 COMUNIDADE", "⚔️ OPERAÇÕES ZVZ",
    "🗣️ COMUNICAÇÃO DE ROLES", "📈 MENTORIA (VODS)",
    "💰 GESTÃO FINANCEIRA", "🔒 ADMINISTRAÇÃO"
]

# --- *** FUNÇÃO create_roles ESTÁ AQUI (Nível do Módulo) *** ---
async def create_roles(guild):
    """Cria todos os cargos necessários e retorna um dicionário."""
    print("Iniciando criação/verificação de Cargos...")
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
    print("Criação/Verificação de Cargos concluída.")
    return r

# --- A Classe Cog (Módulo) ---

class SetupCog(commands.Cog):
    """Cog que contém todos os comandos relacionados ao setup do servidor."""

    def __init__(self, bot):
        self.bot = bot
        print(">>> setup_cog.py (vComLimpeza) FOI LIDO E INICIADO <<<")

    async def delete_existing_structure(self, guild: discord.Guild, message_to_edit: discord.Message):
        """Apaga as categorias e canais gerenciados pelo bot."""
        await message_to_edit.edit(content="PASSO 0/9: Apagando estrutura antiga (categorias e canais)...")
        print("Iniciando limpeza da estrutura antiga...")
        deleted_count = 0
        categories_to_delete = [cat for cat in guild.categories if cat.name in CAT_NAMES]

        for category in categories_to_delete:
            print(f"  Apagando categoria '{category.name}' e seus canais...")
            try:
                channels_in_category = list(category.channels) # Copia a lista para evitar problemas ao iterar e apagar
                for channel in channels_in_category:
                    try:
                        await channel.delete(reason="Recriação da estrutura pelo Bot")
                        deleted_count += 1
                        print(f"    Canal '{channel.name}' apagado.")
                        await asyncio.sleep(0.5)
                    except discord.Forbidden:
                         print(f"    [ERRO DE PERMISSÃO] Não foi possível apagar o canal '{channel.name}'.")
                         # Continua para o próximo canal
                    except Exception as e:
                        print(f"    [ERRO] Falha ao apagar canal '{channel.name}': {e}")

                # Apaga a categoria (agora vazia ou com canais que falharam)
                await category.delete(reason="Recriação da estrutura pelo Bot")
                deleted_count += 1
                print(f"  Categoria '{category.name}' apagada.")
                await asyncio.sleep(0.5)
            except discord.Forbidden:
                 print(f"  [ERRO DE PERMISSÃO] Não foi possível apagar a categoria '{category.name}'.")
                 await message_to_edit.edit(content=f"**ERRO DE PERMISSÃO:** Não foi possível apagar a categoria '{category.name}'. Verifique as permissões do bot e tente novamente.")
                 raise # Interrompe o setup
            except Exception as e:
                print(f"  [ERRO] Falha ao apagar categoria '{category.name}': {e}")


        # Tenta apagar canais órfãos (que podem ter sido criados fora das categorias corretas em execuções anteriores)
        print("  Verificando canais órfãos...")
        all_channel_names = set()
        # Recria a estrutura de nomes de canais esperados
        # (Esta parte precisa ser reconstruída baseada na definição das estruturas abaixo)
        expected_channels_info = self._get_expected_channel_definitions({}) # Passa um dict vazio pois 'roles' não é necessário aqui
        for cat_channels in expected_channels_info.values():
            for ch_info in cat_channels:
                all_channel_names.add(ch_info["name"])

        for channel in guild.channels:
            # Apaga se for canal de texto ou voz, tiver nome esperado e NÃO tiver categoria ou a categoria não for uma das gerenciadas
            if isinstance(channel, (discord.TextChannel, discord.VoiceChannel)) and \
               channel.name in all_channel_names and \
               (channel.category is None or channel.category.name not in CAT_NAMES):
                print(f"    Apagando canal órfão '{channel.name}'...")
                try:
                    await channel.delete(reason="Limpeza de Setup")
                    deleted_count += 1
                    await asyncio.sleep(0.5)
                except Exception as e:
                    print(f"    [ERRO] Falha ao apagar canal órfão '{channel.name}': {e}")


        await message_to_edit.edit(content=f"PASSO 0/9: Limpeza concluída ({deleted_count} itens removidos).")
        print("Limpeza da estrutura antiga concluída.")

    # Função helper para obter definições de canais (evita repetição)
    def _get_expected_channel_definitions(self, roles):
        # Retorna um dicionário onde a chave é o nome da categoria e o valor é a lista de channel_info
        # Preencher com as definições de CADA categoria, como feito no comando setup_servidor abaixo
        # Exemplo para PÚBLICO:
        return {
            "🌎 PÚBLICO": [
                {"name": "📢 | anuncios-publicos", "overwrites": {roles.get("everyone"): discord.PermissionOverwrite(send_messages=False)},
                 "message": "Este é o canal de **Anúncios Públicos**.\n\nFique de olho aqui para novidades importantes sobre o *core* que são abertas a todos."},
                {"name": "✅ | recrutamento", "overwrites": {roles.get("everyone"): discord.PermissionOverwrite(send_messages=True)},
                 "message": "**Bem-vindo ao Recrutamento!**\n\nPara se aplicar ao nosso *core*, por favor, use o comando `/aplicar` (que será configurado no bot) ou aguarde instruções de um Oficial."}
            ],
            "🏁 RECEPÇÃO": [
                 {"name": "🚩 | regras-e-diretrizes", "overwrites": {roles.get("recruta"): discord.PermissionOverwrite(send_messages=False)}, "message": "Seja bem-vindo, Recruta!\n\n**LEITURA OBRIGATÓRIA:**\n\n1. Respeite todos os membros.\n2. Comparecimento em CTAs obrigatórias é essencial.\n3. É obrigatório gravar suas lutas (VODs) para análise.\n4. Regras de Regear estão em `#ℹ️ | info-regear-e-loot` (quando tiver acesso).\n..."},
                 {"name": "👋 | apresente-se", "message": "Use este canal para se apresentar!\n\nDiga-nos seu Nick no jogo, sua(s) classe(s) principal(is), seu fuso horário e um pouco sobre sua experiência em ZvZ."},
                 {"name": "🤖 | comandos-bot", "message": "Use este canal para comandos do bot que podem ser úteis durante o recrutamento, como pedir builds (`!build tank` - será configurado) ou verificar status."}
            ],
            "🌐 COMUNIDADE": [
                 {"name": "📣 | avisos-importantes", "overwrites": {roles.get("mercenario"): discord.PermissionOverwrite(send_messages=False)}, "message": "Canal de **Avisos Importantes** para todos os membros do *core*.\n\nFiquem atentos aqui para anúncios de CTAs, mudanças de regras e outras informações essenciais."},
                 {"name": "💬 | chat-geral", "message": "Este é o *chat-geral*. Sinta-se à vontade para conversar, enviar memes e socializar."},
                 {"name": "🎬 | highlights-e-clips"}, {"name": "💰 | loot-e-sorteios"},
                 {"name": "🎧 Lobby Geral", "is_text": False}
            ],
            "⚔️ OPERAÇÕES ZVZ": [
                 {"name": "❗ | cta-obrigatória", "overwrites": {roles.get("mercenario"): discord.PermissionOverwrite(send_messages=False)}, "message": "Canal para **CTAs Obrigatórias**.\nO bot irá postar as chamadas aqui. Reaja com ✅, ❌ ou ❓."},
                 {"name": "⚔️ | cta-opcional", "overwrites": {roles.get("mercenario"): discord.PermissionOverwrite(send_messages=False)}, "message": "Canal para **CTAs Opcionais**.\nConfirme presença da mesma forma."},
                 {"name": "📅 | registro-cta", "overwrites": {roles.get("mercenario"): discord.PermissionOverwrite(send_messages=False)}, "message": "Este canal é um **log automático** do bot.\nEle mostrará a lista de quem confirmou presença."},
                 {"name": "📜 | builds-oficiais", "overwrites": {roles.get("mercenario"): discord.PermissionOverwrite(send_messages=False)}, "message": "Aqui estarão fixadas as **Builds Oficiais** do *core*.\nUsar a *build* correta é obrigatório."},
                 {"name": "🗺️ | estratégia-e-mapa"}, {"name": "🗣️ Concentração ZvZ", "is_text": False},
                 {"name": "🎙️ COMANDO (Shotcaller)", "is_text": False, "overwrites": { roles.get("everyone"): discord.PermissionOverwrite(read_messages=True, connect=True), roles.get("mercenario"): discord.PermissionOverwrite(speak=False), roles.get("lider"): discord.PermissionOverwrite(speak=True, priority_speaker=True), roles.get("oficial"): discord.PermissionOverwrite(speak=True, priority_speaker=True), roles.get("shotcaller"): discord.PermissionOverwrite(speak=True, priority_speaker=True), roles.get("lider_tank"): discord.PermissionOverwrite(speak=True), roles.get("lider_healer"): discord.PermissionOverwrite(speak=True), roles.get("lider_dps"): discord.PermissionOverwrite(speak=True), roles.get("lider_suporte"): discord.PermissionOverwrite(speak=True), }}
            ],
            "🗣️ COMUNICAÇÃO DE ROLES": [
                 {"name": "🛡️ | chat-tanks", "overwrites": { roles.get("tank"): discord.PermissionOverwrite(read_messages=True) }},
                 {"name": "💚 | chat-healers", "overwrites": { roles.get("healer"): discord.PermissionOverwrite(read_messages=True) }},
                 {"name": "💥 | chat-dps", "overwrites": { roles.get("dps"): discord.PermissionOverwrite(read_messages=True) }},
                 {"name": "✨ | chat-suporte", "overwrites": { roles.get("suporte"): discord.PermissionOverwrite(read_messages=True) }}
            ],
             "📈 MENTORIA (VODS)": [
                 {"name": "ℹ️ | como-gravar-e-postar", "overwrites": { roles.get("mercenario"): discord.PermissionOverwrite(send_messages=False) }, "message": "**Tutorial de Gravação (VODs)**\n\nÉ obrigatório gravar suas ZvZs.\n1. **Software:** Use OBS Studio, Nvidia ShadowPlay ou AMD ReLive.\n2. **Upload:** Envie o vídeo para o YouTube como 'Não Listado'.\n3. **Postagem:** Cole o link no canal da sua *role* (ex: `#🛡️ | vods-tank`)."},
                 {"name": "🧑‍🏫 | feedback-dos-coaches", "overwrites": { roles.get("mercenario"): discord.PermissionOverwrite(send_messages=False), roles.get("coach"): discord.PermissionOverwrite(send_messages=True), roles.get("oficial"): discord.PermissionOverwrite(send_messages=True), }, "message": "Canal para os **Coaches e Líderes** darem *feedback* geral.\n(Apenas Coaches/Oficiais podem escrever aqui)."},
                 {"name": "🛡️ | vods-tank"}, {"name": "💚 | vods-healer"},
                 {"name": "💥 | vods-dps"}, {"name": "✨ | vods-suporte"},
                 {"name": "📺 Sala de Análise 1", "is_text": False},
                 {"name": "📺 Sala de Análise 2", "is_text": False}
             ],
            "💰 GESTÃO FINANCEIRA": [
                 {"name": "ℹ️ | info-regear-e-loot", "overwrites": { roles.get("mercenario"): discord.PermissionOverwrite(send_messages=False) }, "message": "**Regras de Regear e Loot Split**\n\n**Regear:**\n1. O *core* cobre *regears* (T8.3 eq.) em CTAs **obrigatórias**.\n2. Para solicitar, use `/regear` em `#📦 | solicitar-regear`.\n3. Aguarde aprovação.\n\n**Loot Split:**\n1. Todo *loot* ZvZ é recolhido.\n2. Taxa de X% retida.\n3. Restante dividido entre presentes e pago semanalmente."},
                 {"name": "📦 | solicitar-regear", "message": "Use este canal **apenas** para usar o comando `/regear` e anexar o *screenshot* da sua morte.\nAguarde a reação ✅ ou ❌ de um Oficial."},
                 {"name": "🧾 | lootsplit-e-pagamentos", "overwrites": { roles.get("mercenario"): discord.PermissionOverwrite(send_messages=False) }, "message": "Canal para a liderança postar os relatórios de **Loot Split** e confirmar pagamentos."}
             ],
             "🔒 ADMINISTRAÇÃO": [
                 {"name": "💬 | chat-liderança"}, {"name": "📊 | gerenciamento-core"},
                 {"name": "✅ | regears-aprovados"}, {"name": "🤖 | logs-do-bot"},
                 {"name": "🔒 Reunião de Oficiais", "is_text": False}
             ]
        }


    @app_commands.command( name="setup-servidor", description="APAGA TUDO e recria a estrutura do servidor. (Apenas Admins)")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_servidor(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "⚠️ **AVISO:** Este comando irá **APAGAR** as categorias e canais gerenciados pelo bot e recriá-los do zero!\n"
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
        main_message = await interaction.followup.send(f"🔥 Confirmado! Iniciando a recriação completa do servidor '{guild.name}'...")

        try:
            # PASSO 0: Apagar Estrutura Antiga
            await self.delete_existing_structure(guild, main_message)

            # PASSO 1: Criar Cargos
            await main_message.edit(content="PASSO 1/9: Verificando/Criando cargos...")
            roles = await create_roles(guild) # A CHAMADA ESTÁ AQUI

            # --- PASSO 2 a 9: Recriar Categorias e Canais ---
            # Define a estrutura aqui para passar para a função de criação
            # (Adicione as permissões de categoria onde necessário)
            ow_cat_recepcao = { roles.get("everyone"): discord.PermissionOverwrite(read_messages=False), roles.get("recruta"): discord.PermissionOverwrite(read_messages=True), roles.get("mercenario"): discord.PermissionOverwrite(read_messages=False), roles.get("oficial"): discord.PermissionOverwrite(read_messages=True), }
            ow_cat_comunidade = { roles.get("everyone"): discord.PermissionOverwrite(read_messages=False), roles.get("mercenario"): discord.PermissionOverwrite(read_messages=True), roles.get("oficial"): discord.PermissionOverwrite(read_messages=True), }
            ow_cat_zvz = { roles.get("everyone"): discord.PermissionOverwrite(read_messages=False), roles.get("mercenario"): discord.PermissionOverwrite(read_messages=True), roles.get("oficial"): discord.PermissionOverwrite(read_messages=True), }
            ow_cat_roles = { roles.get("everyone"): discord.PermissionOverwrite(read_messages=False), roles.get("mercenario"): discord.PermissionOverwrite(read_messages=False), roles.get("oficial"): discord.PermissionOverwrite(read_messages=True), roles.get("coach"): discord.PermissionOverwrite(read_messages=True), }
            ow_cat_mentoria = { roles.get("everyone"): discord.PermissionOverwrite(read_messages=False), roles.get("mercenario"): discord.PermissionOverwrite(read_messages=True), roles.get("oficial"): discord.PermissionOverwrite(read_messages=True), }
            ow_cat_fin = { roles.get("everyone"): discord.PermissionOverwrite(read_messages=False), roles.get("mercenario"): discord.PermissionOverwrite(read_messages=True), roles.get("oficial"): discord.PermissionOverwrite(read_messages=True), }
            ow_cat_admin = { roles.get("everyone"): discord.PermissionOverwrite(read_messages=False), roles.get("mercenario"): discord.PermissionOverwrite(read_messages=False), roles.get("oficial"): discord.PermissionOverwrite(read_messages=True), roles.get("lider"): discord.PermissionOverwrite(read_messages=True), }

            # Obtém todas as definições de canais
            all_definitions = self._get_expected_channel_definitions(roles)

            # Lista ordenada de categorias para criação
            categorias_para_criar = [
                ("🌎 PÚBLICO", None), ("🏁 RECEPÇÃO", ow_cat_recepcao), ("🌐 COMUNIDADE", ow_cat_comunidade),
                ("⚔️ OPERAÇÕES ZVZ", ow_cat_zvz), ("🗣️ COMUNICAÇÃO DE ROLES", ow_cat_roles),
                ("📈 MENTORIA (VODS)", ow_cat_mentoria), ("💰 GESTÃO FINANCEIRA", ow_cat_fin),
                ("🔒 ADMINISTRAÇÃO", ow_cat_admin)
            ]

            for i, (cat_name, cat_overwrites) in enumerate(categorias_para_criar):
                 step_num = i + 2
                 await main_message.edit(content=f"PASSO {step_num}/9: Recriando Categoria: {cat_name}...")
                 channels_list = all_definitions.get(cat_name, [])
                 if not channels_list:
                     print(f"  [AVISO] Nenhuma definição de canal encontrada para a categoria '{cat_name}'.")
                     continue # Pula para a próxima categoria se não houver canais definidos

                 # Passa as permissões corretas da categoria para a função
                 await create_category_and_channels(guild, cat_name, channels_list, roles, cat_overwrites)
                 await asyncio.sleep(0.5)


            await main_message.edit(content="🚀 **Recriação Completa do Servidor Concluída!** 🚀")

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