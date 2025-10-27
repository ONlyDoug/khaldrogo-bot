import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import get
import asyncio
import traceback

# --- Funções Auxiliares de Criação (Idempotentes não são mais o foco principal, mas mantidas) ---
# (As funções get_or_create_role, get_or_create_category, get_or_create_channel permanecem as mesmas da versão anterior)
async def get_or_create_role(guild: discord.Guild, name: str, **kwargs):
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
    existing_cat = discord.utils.get(guild.categories, name=name)
    if existing_cat:
        print(f"  [SKIP] Categoria '{name}' já existe (será apagada).")
        # Não retorna mais a existente, pois será apagada
    print(f"  [CREATE] Preparando para criar Categoria '{name}'...")
    # A criação será feita após a limpeza
    return None # Retorna None para indicar que a criação será posterior

async def create_category_and_channels(guild: discord.Guild, name: str, channels_to_create: list, roles: dict, overwrites_cat: dict = None):
    """Cria uma categoria e seus canais associados."""
    print(f"  [CREATE] Criando Categoria '{name}'...")
    try:
        category = await guild.create_category(name=name, overwrites=overwrites_cat or {})
        await asyncio.sleep(0.5) # Pausa para evitar rate limit
    except Exception as e:
        print(f"  [ERRO] Falha ao criar categoria '{name}': {e}")
        return None # Retorna None se a categoria falhar

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
                    # Verifica se o canal está realmente vazio antes de enviar (redundância)
                    await asyncio.sleep(0.2) # Pequena pausa
                    if not [msg async for msg in channel.history(limit=1)]:
                        await channel.send(initial_message)
            else: # Canal de Voz
                await category.create_voice_channel(name=ch_name, overwrites=overwrites_ch)
            await asyncio.sleep(0.3) # Pausa entre canais
        except Exception as e:
            print(f"      [ERRO] Falha ao criar canal '{ch_name}': {e}")
            # Continua para os próximos canais mesmo se um falhar

    return category

# --- Nomes das Categorias (Corrigidos) ---
CAT_NAMES = [
    "🌎 PÚBLICO", "🏁 RECEPÇÃO", "🌐 COMUNIDADE", "⚔️ OPERAÇÕES ZVZ",
    "🗣️ COMUNICAÇÃO DE ROLES", "📈 MENTORIA (VODS)",
    "💰 GESTÃO FINANCEIRA", "🔒 ADMINISTRAÇÃO"
]

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
                # Apaga canais primeiro (mais seguro contra rate limits)
                for channel in category.channels:
                    try:
                        await channel.delete(reason="Recriação da estrutura pelo Bot")
                        deleted_count += 1
                        print(f"    Canal '{channel.name}' apagado.")
                        await asyncio.sleep(0.5) # Pausa
                    except Exception as e:
                        print(f"    [ERRO] Falha ao apagar canal '{channel.name}': {e}")
                # Apaga a categoria vazia
                await category.delete(reason="Recriação da estrutura pelo Bot")
                deleted_count += 1
                print(f"  Categoria '{category.name}' apagada.")
                await asyncio.sleep(0.5) # Pausa
            except discord.Forbidden:
                 print(f"  [ERRO DE PERMISSÃO] Não foi possível apagar a categoria '{category.name}'. Verifique as permissões do bot.")
                 await message_to_edit.edit(content=f"**ERRO DE PERMISSÃO:** Não foi possível apagar a categoria '{category.name}'. Verifique as permissões do bot e tente novamente.")
                 raise # Interrompe o setup se não puder apagar
            except Exception as e:
                print(f"  [ERRO] Falha ao apagar categoria '{category.name}': {e}")
                # Considerar se deve parar ou continuar

        await message_to_edit.edit(content=f"PASSO 0/9: Limpeza concluída ({deleted_count} itens removidos).")
        print("Limpeza da estrutura antiga concluída.")


    @app_commands.command( name="setup-servidor", description="APAGA TUDO e recria a estrutura do servidor. (Apenas Admins)")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_servidor(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "⚠️ **AVISO:** Este comando irá **APAGAR** as categorias e canais gerenciados pelo bot e recriá-los do zero!\n"
            "Confirme digitando `SIM APAGAR TUDO` no chat em 30 segundos.",
            ephemeral=True
        )

        def check(m):
            # Verifica se a mensagem é do mesmo autor, no mesmo canal e tem o conteúdo exato
            return m.author == interaction.user and m.channel == interaction.channel and m.content == "SIM APAGAR TUDO"

        try:
            confirmation_msg = await self.bot.wait_for('message', timeout=30.0, check=check)
            try:
                await confirmation_msg.delete() # Apaga a mensagem de confirmação
            except: pass # Ignora se não puder apagar
        except asyncio.TimeoutError:
            await interaction.followup.send("Comando cancelado. Nenhuma alteração foi feita.", ephemeral=True)
            return
        except Exception as e:
             await interaction.followup.send(f"Erro inesperado durante a confirmação: {e}", ephemeral=True)
             return

        # ---- INÍCIO DA EXECUÇÃO REAL ----
        guild = interaction.guild
        main_message = await interaction.followup.send(f"🔥 Confirmado! Iniciando a recriação completa do servidor '{guild.name}'...")

        try:
            # PASSO 0: Apagar Estrutura Antiga
            await self.delete_existing_structure(guild, main_message)

            # PASSO 1: Criar Cargos (Idempotente ainda útil aqui)
            await main_message.edit(content="PASSO 1/9: Verificando/Criando cargos...")
            # create_roles deve estar disponível no módulo; se não estiver, adicione/importe.
            roles = await create_roles(guild)

            # --- PASSO 2 a 9: Recriar Categorias e Canais ---

            # 2. PÚBLICO
            await main_message.edit(content="PASSO 2/9: Recriando Categoria: 🌎 PÚBLICO...")
            channels_publico = [
                {"name": "📢 | anuncios-publicos", "overwrites": {roles["everyone"]: discord.PermissionOverwrite(send_messages=False)},
                 "message": "Este é o canal de **Anúncios Públicos**.\n\nFique de olho aqui para novidades importantes sobre o *core* que são abertas a todos."},
                {"name": "✅ | recrutamento", "overwrites": {roles["everyone"]: discord.PermissionOverwrite(send_messages=True)},
                 "message": "**Bem-vindo ao Recrutamento!**\n\nPara se aplicar ao nosso *core*, por favor, use o comando `/aplicar` (que será configurado no bot) ou aguarde instruções de um Oficial."}
            ]
            await create_category_and_channels(guild, "🌎 PÚBLICO", channels_publico, roles)

            # 3. RECEPÇÃO
            await main_message.edit(content="PASSO 3/9: Recriando Categoria: 🏁 RECEPÇÃO...")
            ow_cat_recepcao = { roles["everyone"]: discord.PermissionOverwrite(read_messages=False), roles["recruta"]: discord.PermissionOverwrite(read_messages=True), roles["mercenario"]: discord.PermissionOverwrite(read_messages=False), roles["oficial"]: discord.PermissionOverwrite(read_messages=True), }
            channels_recepcao = [
                {"name": "🚩 | regras-e-diretrizes", "overwrites": {roles["recruta"]: discord.PermissionOverwrite(send_messages=False)},
                 "message": "Seja bem-vindo, Recruta!\n\n**LEITURA OBRIGATÓRIA:**\n\n1. Respeite todos os membros.\n2. Comparecimento em CTAs obrigatórias é essencial.\n3. É obrigatório gravar suas lutas (VODs) para análise.\n4. Regras de Regear estão em `#ℹ️ | info-regear-e-loot` (quando tiver acesso).\n..."},
                {"name": "👋 | apresente-se",
                 "message": "Use este canal para se apresentar!\n\nDiga-nos seu Nick no jogo, sua(s) classe(s) principal(is), seu fuso horário e um pouco sobre sua experiência em ZvZ."},
                {"name": "🤖 | comandos-bot",
                 "message": "Use este canal para comandos do bot que podem ser úteis durante o recrutamento, como pedir builds (`!build tank` - será configurado) ou verificar status."}
            ]
            await create_category_and_channels(guild, "🏁 RECEPÇÃO", channels_recepcao, roles, ow_cat_recepcao)

            # 4. COMUNIDADE
            await main_message.edit(content="PASSO 4/9: Recriando Categoria: 🌐 COMUNIDADE...")
            ow_cat_comunidade = { roles["everyone"]: discord.PermissionOverwrite(read_messages=False), roles["mercenario"]: discord.PermissionOverwrite(read_messages=True), roles["oficial"]: discord.PermissionOverwrite(read_messages=True), }
            channels_comunidade = [
                 {"name": "📣 | avisos-importantes", "overwrites": {roles["mercenario"]: discord.PermissionOverwrite(send_messages=False)},
                  "message": "Canal de **Avisos Importantes** para todos os membros do *core*.\n\nFiquem atentos aqui para anúncios de CTAs, mudanças de regras e outras informações essenciais."},
                 {"name": "💬 | chat-geral", "message": "Este é o *chat-geral*. Sinta-se à vontade para conversar, enviar memes e socializar."},
                 {"name": "🎬 | highlights-e-clips"},
                 {"name": "💰 | loot-e-sorteios"},
                 {"name": "🎧 Lobby Geral", "is_text": False}
            ]
            await create_category_and_channels(guild, "🌐 COMUNIDADE", channels_comunidade, roles, ow_cat_comunidade)

            # 5. OPERAÇÕES ZVZ
            await main_message.edit(content="PASSO 5/9: Recriando Categoria: ⚔️ OPERAÇÕES ZVZ...")
            ow_cat_zvz = { roles["everyone"]: discord.PermissionOverwrite(read_messages=False), roles["mercenario"]: discord.PermissionOverwrite(read_messages=True), roles["oficial"]: discord.PermissionOverwrite(read_messages=True), }
            ow_ch_cta_read_only = { roles["mercenario"]: discord.PermissionOverwrite(send_messages=False) }
            ow_ch_comando_voz = { roles["everyone"]: discord.PermissionOverwrite(read_messages=True, connect=True), roles["mercenario"]: discord.PermissionOverwrite(speak=False), roles["lider"]: discord.PermissionOverwrite(speak=True, priority_speaker=True), roles["oficial"]: discord.PermissionOverwrite(speak=True, priority_speaker=True), roles["shotcaller"]: discord.PermissionOverwrite(speak=True, priority_speaker=True), roles["lider_tank"]: discord.PermissionOverwrite(speak=True), roles["lider_healer"]: discord.PermissionOverwrite(speak=True), roles["lider_dps"]: discord.PermissionOverwrite(speak=True), roles["lider_suporte"]: discord.PermissionOverwrite(speak=True), }
            channels_zvz = [
                {"name": "❗ | cta-obrigatória", "overwrites": ow_ch_cta_read_only, "message": "Canal para **CTAs Obrigatórias**.\nO bot irá postar as chamadas aqui. Reaja com ✅, ❌ ou ❓."},
                {"name": "⚔️ | cta-opcional", "overwrites": ow_ch_cta_read_only, "message": "Canal para **CTAs Opcionais**.\nConfirme presença da mesma forma."},
                {"name": "📅 | registro-cta", "overwrites": ow_ch_cta_read_only, "message": "Este canal é um **log automático** do bot.\nEle mostrará a lista de quem confirmou presença."},
                {"name": "📜 | builds-oficiais", "overwrites": ow_ch_cta_read_only, "message": "Aqui estarão fixadas as **Builds Oficiais** do *core*.\nUsar a *build* correta é obrigatório."},
                {"name": "🗺️ | estratégia-e-mapa"},
                {"name": "🗣️ Concentração ZvZ", "is_text": False},
                {"name": "🎙️ COMANDO (Shotcaller)", "is_text": False, "overwrites": ow_ch_comando_voz}
            ]
            await create_category_and_channels(guild, "⚔️ OPERAÇÕES ZVZ", channels_zvz, roles, ow_cat_zvz)

            # 6. COMUNICAÇÃO DE ROLES
            await main_message.edit(content="PASSO 6/9: Recriando Categoria: 🗣️ COMUNICAÇÃO DE ROLES...")
            ow_cat_roles = { roles["everyone"]: discord.PermissionOverwrite(read_messages=False), roles["mercenario"]: discord.PermissionOverwrite(read_messages=False), roles["oficial"]: discord.PermissionOverwrite(read_messages=True), roles["coach"]: discord.PermissionOverwrite(read_messages=True), }
            channels_roles = [
                {"name": "🛡️ | chat-tanks", "overwrites": { roles["tank"]: discord.PermissionOverwrite(read_messages=True), **ow_cat_roles }},
                {"name": "💚 | chat-healers", "overwrites": { roles["healer"]: discord.PermissionOverwrite(read_messages=True), **ow_cat_roles }},
                {"name": "💥 | chat-dps", "overwrites": { roles["dps"]: discord.PermissionOverwrite(read_messages=True), **ow_cat_roles }},
                {"name": "✨ | chat-suporte", "overwrites": { roles["suporte"]: discord.PermissionOverwrite(read_messages=True), **ow_cat_roles }}
            ]
            await create_category_and_channels(guild, "🗣️ COMUNICAÇÃO DE ROLES", channels_roles, roles, ow_cat_roles)

            # 7. MENTORIA (VODS)
            await main_message.edit(content="PASSO 7/9: Recriando Categoria: 📈 MENTORIA (VODS)...")
            ow_cat_mentoria = { roles["everyone"]: discord.PermissionOverwrite(read_messages=False), roles["mercenario"]: discord.PermissionOverwrite(read_messages=True), roles["oficial"]: discord.PermissionOverwrite(read_messages=True), }
            ow_ch_info_vod = { roles["mercenario"]: discord.PermissionOverwrite(send_messages=False) }
            ow_ch_feedback_vod = { roles["mercenario"]: discord.PermissionOverwrite(send_messages=False), roles["coach"]: discord.PermissionOverwrite(send_messages=True), roles["oficial"]: discord.PermissionOverwrite(send_messages=True), }
            channels_mentoria = [
                {"name": "ℹ️ | como-gravar-e-postar", "overwrites": ow_ch_info_vod, "message": "**Tutorial de Gravação (VODs)**\n\nÉ obrigatório gravar suas ZvZs.\n1. **Software:** Use OBS Studio, Nvidia ShadowPlay ou AMD ReLive.\n2. **Upload:** Envie o vídeo para o YouTube como 'Não Listado'.\n3. **Postagem:** Cole o link no canal da sua *role* (ex: `#🛡️ | vods-tank`)."},
                {"name": "🧑‍🏫 | feedback-dos-coaches", "overwrites": ow_ch_feedback_vod, "message": "Canal para os **Coaches e Líderes** darem *feedback* geral.\n(Apenas Coaches/Oficiais podem escrever aqui)."},
                {"name": "🛡️ | vods-tank"}, {"name": "💚 | vods-healer"},
                {"name": "💥 | vods-dps"}, {"name": "✨ | vods-suporte"},
                {"name": "📺 Sala de Análise 1", "is_text": False},
                {"name": "📺 Sala de Análise 2", "is_text": False}
            ]
            await create_category_and_channels(guild, "📈 MENTORIA (VODS)", channels_mentoria, roles, ow_cat_mentoria)

            # 8. GESTÃO FINANCEIRA
            await main_message.edit(content="PASSO 8/9: Recriando Categoria: 💰 GESTÃO FINANCEIRA...")
            ow_cat_fin = { roles["everyone"]: discord.PermissionOverwrite(read_messages=False), roles["mercenario"]: discord.PermissionOverwrite(read_messages=True), roles["oficial"]: discord.PermissionOverwrite(read_messages=True), }
            ow_ch_info_fin = { roles["mercenario"]: discord.PermissionOverwrite(send_messages=False) }
            channels_financeiro = [
                {"name": "ℹ️ | info-regear-e-loot", "overwrites": ow_ch_info_fin, "message": "**Regras de Regear e Loot Split**\n\n**Regear:**\n1. O *core* cobre *regears* (T8.3 eq.) em CTAs **obrigatórias**.\n2. Para solicitar, use `/regear` em `#📦 | solicitar-regear`.\n3. Aguarde aprovação.\n\n**Loot Split:**\n1. Todo *loot* ZvZ é recolhido.\n2. Taxa de X% retida.\n3. Restante dividido entre presentes e pago semanalmente."},
                {"name": "📦 | solicitar-regear", "message": "Use este canal **apenas** para usar o comando `/regear` e anexar o *screenshot* da sua morte.\nAguarde a reação ✅ ou ❌ de um Oficial."},
                {"name": "🧾 | lootsplit-e-pagamentos", "overwrites": ow_ch_info_fin, "message": "Canal para a liderança postar os relatórios de **Loot Split** e confirmar pagamentos."}
            ]
            await create_category_and_channels(guild, "💰 GESTÃO FINANCEIRA", channels_financeiro, roles, ow_cat_fin)

            # 9. ADMINISTRAÇÃO
            await main_message.edit(content="PASSO 9/9: Recriando Categoria: 🔒 ADMINISTRAÇÃO...")
            ow_cat_admin = { roles["everyone"]: discord.PermissionOverwrite(read_messages=False), roles["mercenario"]: discord.PermissionOverwrite(read_messages=False), roles["oficial"]: discord.PermissionOverwrite(read_messages=True), roles["lider"]: discord.PermissionOverwrite(read_messages=True), }
            channels_admin = [
                {"name": "💬 | chat-liderança"}, {"name": "📊 | gerenciamento-core"},
                {"name": "✅ | regears-aprovados"}, {"name": "🤖 | logs-do-bot"},
                {"name": "🔒 Reunião de Oficiais", "is_text": False}
            ]
            await create_category_and_channels(guild, "🔒 ADMINISTRAÇÃO", channels_admin, roles, ow_cat_admin)

            await main_message.edit(content="🚀 **Recriação Completa do Servidor Concluída!** 🚀")

        except discord.Forbidden:
            await main_message.edit(content="**ERRO DE PERMISSÃO DURANTE A CRIAÇÃO:** O Bot não tem permissão para 'Gerir Cargos' ou 'Gerir Canais'. Verifique as permissões e tente novamente.")
            traceback.print_exc()
        except Exception as e:
            await main_message.edit(content=f"**ERRO INESPERADO DURANTE A CRIAÇÃO:** A configuração falhou.\nVerifique os logs.\n`{type(e).__name__}: {e}`")
            print(f"Erro detalhado no comando '/setup-servidor':")
            traceback.print_exc()

    @setup_servidor.error
    async def setup_servidor_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        # (O error handler permanece o mesmo da versão anterior)
        if isinstance(error, app_commands.MissingPermissions):
             if not interaction.response.is_done(): await interaction.response.send_message("Apenas administradores podem usar este comando.", ephemeral=True)
             else: await interaction.followup.send("Apenas administradores podem usar este comando.", ephemeral=True)
        else:
            send_func = interaction.followup.send if interaction.response.is_done() else interaction.response.send_message
            try:
                await send_func(f"Ocorreu um erro inesperado: {type(error).__name__}", ephemeral=True)
            except discord.NotFound: print("Erro no setup_servidor_error: Interação expirou.")
            except Exception as e: print(f"Erro ao enviar msg de erro no setup_servidor_error: {e}")
            print(f"Erro não tratado no comando '/setup-servidor':")
            traceback.print_exc()

async def setup(bot):
    await bot.add_cog(SetupCog(bot))