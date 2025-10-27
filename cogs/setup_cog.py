import discord
from discord.ext import commands

# --- Funções Auxiliares de Criação ---
# (Aqui estão as funções que criam os cargos, canais e permissões)

async def create_roles(guild):
    """Cria todos os cargos necessários e retorna um dicionário."""
    
    # Cargos de Hierarquia
    r_recruta = await guild.create_role(name="Recruta", colour=discord.Colour.light_grey())
    r_mercenario = await guild.create_role(name="Mercenário", colour=discord.Colour.green())
    r_coach = await guild.create_role(name="Coach", colour=discord.Colour.blue())
    r_shotcaller = await guild.create_role(name="Shotcaller", colour=discord.Colour.gold())
    r_oficial = await guild.create_role(name="Oficial", colour=discord.Colour.purple())
    r_lider = await guild.create_role(name="Líder", colour=discord.Colour.red())

    # Cargos de Role
    r_tank = await guild.create_role(name="Tank", colour=discord.Colour(0x607d8b)) # Cinza
    r_healer = await guild.create_role(name="Healer", colour=discord.Colour(0x4caf50)) # Verde
    r_dps = await guild.create_role(name="DPS", colour=discord.Colour(0xf44336)) # Vermelho
    r_suporte = await guild.create_role(name="Suporte", colour=discord.Colour(0x9c27b0)) # Roxo

    # Cargos de Comunicação ZvZ
    r_lider_tank = await guild.create_role(name="Líder-Tank")
    r_lider_healer = await guild.create_role(name="Líder-Healer")
    r_lider_dps = await guild.create_role(name="Líder-DPS")
    r_lider_suporte = await guild.create_role(name="Líder-Suporte")

    return {
        "everyone": guild.default_role,
        "recruta": r_recruta,
        "mercenario": r_mercenario,
        "coach": r_coach,
        "shotcaller": r_shotcaller,
        "oficial": r_oficial,
        "lider": r_lider,
        "tank": r_tank,
        "healer": r_healer,
        "dps": r_dps,
        "suporte": r_suporte,
        "lider_tank": r_lider_tank,
        "lider_healer": r_lider_healer,
        "lider_dps": r_lider_dps,
        "lider_suporte": r_lider_suporte,
    }

async def setup_publico(guild, roles):
    """Cria a Categoria PÚBLICO"""
    cat = await guild.create_category("🌎 CATEGORIA: PÚBLICO")
    
    ch = await cat.create_text_channel(
        "📢 | anuncios-publicos",
        overwrites={ roles["everyone"]: discord.PermissionOverwrite(read_messages=True, send_messages=False) }
    )
    await ch.send("Este é o canal de **Anúncios Públicos**.\n\nFique de olho aqui para novidades importantes sobre o *core* que são abertas a todos.")

    ch = await cat.create_text_channel("✅ | recrutamento")
    await ch.send("**Bem-vindo ao Recrutamento!**\n\nPara se aplicar ao nosso *core*, por favor, use o comando `/aplicar` (que será configurado no bot) ou aguarde instruções de um Oficial.")

async def setup_recepcao(guild, roles):
    """Cria a Categoria RECEPÇÃO (Privada para Recrutas)"""
    cat = await guild.create_category(
        "🏁 CATEGORIA: RECEPÇÃO",
        overwrites={
            roles["everyone"]: discord.PermissionOverwrite(read_messages=False),
            roles["recruta"]: discord.PermissionOverwrite(read_messages=True),
            roles["mercenario"]: discord.PermissionOverwrite(read_messages=False),
            roles["oficial"]: discord.PermissionOverwrite(read_messages=True),
        }
    )
    
    ch = await cat.create_text_channel(
        "🚩 | regras-e-diretrizes",
        overwrites={ roles["recruta"]: discord.PermissionOverwrite(send_messages=False) }
    )
    await ch.send("Seja bem-vindo, Recruta!\n\n**LEITURA OBRIGATÓRIA:**\n\n1.  Respeite todos os membros.\n2.  Comparecimento em CTAs obrigatórias é essencial.\n3.  É obrigatório gravar suas lutas (VODs) para análise.\n4.  Regras de Regear estão em #ℹ️ | info-regear-e-loot.\n...")

    ch = await cat.create_text_channel("👋 | apresente-se")
    await ch.send("Use este canal para se apresentar!\n\nDiga-nos seu Nick no jogo, sua(s) classe(s) principal(is), seu fuso horário e um pouco sobre sua experiência em ZvZ.")
    
    ch = await cat.create_text_channel("🤖 | comandos-bot")
    await ch.send("Use este canal para comandos do bot, como pedir builds (`!build tank`) ou verificar seus status.")

async def setup_comunidade(guild, roles):
    """Cria a Categoria COMUNIDADE (Privada para Mercenários)"""
    cat = await guild.create_category(
        "🌐 CATEGORIA: COMUNIDADE",
        overwrites={
            roles["everyone"]: discord.PermissionOverwrite(read_messages=False),
            roles["mercenario"]: discord.PermissionOverwrite(read_messages=True),
            roles["oficial"]: discord.PermissionOverwrite(read_messages=True),
        }
    )

    ch = await cat.create_text_channel(
        "📣 | avisos-importantes",
        overwrites={ roles["mercenario"]: discord.PermissionOverwrite(send_messages=False) }
    )
    await ch.send("Canal de **Avisos Importantes** para todos os membros do *core*.\n\nFiquem atentos aqui para anúncios de CTAs, mudanças de regras e outras informações essenciais.")

    ch = await cat.create_text_channel("💬 | chat-geral")
    await ch.send("Este é o *chat-geral*. Sinta-se à vontade para conversar, enviar memes e socializar.")

    await cat.create_text_channel("🎬 | highlights-e-clips")
    await cat.create_text_channel("💰 | loot-e-sorteios")
    await cat.create_voice_channel("🎧 Lobby Geral")

async def setup_zvz(guild, roles):
    """Cria a Categoria OPERAÇÕES ZVZ (Privada para Mercenários)"""
    cat = await guild.create_category(
        "⚔️ CATEGORIA: OPERAÇÕES ZVZ",
        overwrites={
            roles["everyone"]: discord.PermissionOverwrite(read_messages=False),
            roles["mercenario"]: discord.PermissionOverwrite(read_messages=True),
            roles["oficial"]: discord.PermissionOverwrite(read_messages=True),
        }
    )

    ch = await cat.create_text_channel(
        "❗ | cta-obrigatória",
        overwrites={ roles["mercenario"]: discord.PermissionOverwrite(send_messages=False) }
    )
    await ch.send("Canal para **CTAs Obrigatórias** (Territórios, Castelos, etc.).\n\nO bot irá postar as chamadas aqui. Reaja com ✅ (Presente), ❌ (Ausente) ou ❓ (Dúvida).")

    ch = await cat.create_text_channel(
        "⚔️ | cta-opcional",
        overwrites={ roles["mercenario"]: discord.PermissionOverwrite(send_messages=False) }
    )
    await ch.send("Canal para **CTAs Opcionais** (Fame Farm, Gank, Conteúdo secundário).\n\nConfirme presença da mesma forma.")
    
    ch = await cat.create_text_channel(
        "📅 | registro-cta",
        overwrites={ roles["mercenario"]: discord.PermissionOverwrite(send_messages=False) }
    )
    await ch.send("Este canal é um **log automático** do bot.\n\nEle mostrará a lista de quem confirmou presença nas CTAs para facilitar a organização dos líderes.")

    ch = await cat.create_text_channel(
        "📜 | builds-oficiais",
        overwrites={ roles["mercenario"]: discord.PermissionOverwrite(send_messages=False) }
    )
    await ch.send("Aqui estarão fixadas as **Builds Oficiais** do *core*.\n\nUsar a *build* correta é obrigatório. Use o comando `!build [role]` para ver a sua.")

    await cat.create_text_channel("🗺️ | estratégia-e-mapa")
    
    await cat.create_voice_channel("🗣️ Concentração ZvZ")
    
    ch_comando_overwrites = {
        roles["everyone"]: discord.PermissionOverwrite(read_messages=True, connect=True),
        roles["mercenario"]: discord.PermissionOverwrite(speak=False), # Mercenário NÃO FALA
        roles["lider"]: discord.PermissionOverwrite(speak=True, priority_speaker=True),
        roles["oficial"]: discord.PermissionOverwrite(speak=True, priority_speaker=True),
        roles["shotcaller"]: discord.PermissionOverwrite(speak=True, priority_speaker=True),
        roles["lider_tank"]: discord.PermissionOverwrite(speak=True), 
        roles["lider_healer"]: discord.PermissionOverwrite(speak=True),
        roles["lider_dps"]: discord.PermissionOverwrite(speak=True),
        roles["lider_suporte"]: discord.PermissionOverwrite(speak=True),
    }
    await cat.create_voice_channel(
        "🎙️ COMANDO (Shotcaller)",
        overwrites=ch_comando_overwrites
    )

async def setup_roles_chat(guild, roles):
    """Cria a Categoria COMUNICAÇÃO DE ROLES (Privada por Role)"""
    base_overwrites = {
        roles["everyone"]: discord.PermissionOverwrite(read_messages=False),
        roles["mercenario"]: discord.PermissionOverwrite(read_messages=False), 
        roles["oficial"]: discord.PermissionOverwrite(read_messages=True), 
        roles["coach"]: discord.PermissionOverwrite(read_messages=True), 
    }
    cat = await guild.create_category(
        "🗣️ CATEGORIA: COMUNICAÇÃO DE ROLES",
        overwrites=base_overwrites
    )

    await cat.create_text_channel(
        "🛡️ | chat-tanks",
        overwrites={ roles["tank"]: discord.PermissionOverwrite(read_messages=True) }
    )
    await cat.create_text_channel(
        "💚 | chat-healers",
        overwrites={ roles["healer"]: discord.PermissionOverwrite(read_messages=True) }
    )
    await cat.create_text_channel(
        "💥 | chat-dps",
        overwrites={ roles["dps"]: discord.PermissionOverwrite(read_messages=True) }
    )
    await cat.create_text_channel(
        "✨ | chat-suporte",
        overwrites={ roles["suporte"]: discord.PermissionOverwrite(read_messages=True) }
    )

async def setup_mentoria(guild, roles):
    """Cria a Categoria MENTORIA (VODS)"""
    cat = await guild.create_category(
        "📈 CATEGORIA: MENTORIA (VODS)",
        overwrites={
            roles["everyone"]: discord.PermissionOverwrite(read_messages=False),
            roles["mercenario"]: discord.PermissionOverwrite(read_messages=True),
            roles["oficial"]: discord.PermissionOverwrite(read_messages=True),
        }
    )
    
    ch = await cat.create_text_channel(
        "ℹ️ | como-gravar-e-postar",
        overwrites={ roles["mercenario"]: discord.PermissionOverwrite(send_messages=False) }
    )
    await ch.send("**Tutorial de Gravação (VODs)**\n\nÉ obrigatório gravar suas ZvZs.\n1.  **Software:** Use OBS Studio, Nvidia ShadowPlay ou AMD ReLive.\n2.  **Upload:** Envie o vídeo para o YouTube como 'Não Listado'.\n3.  **Postagem:** Cole o link do YouTube no canal da sua *role* (ex: #🛡️ | vods-tank) após a ZvZ.")

    ch = await cat.create_text_channel(
        "🧑‍🏫 | feedback-dos-coaches",
        overwrites={
            roles["mercenario"]: discord.PermissionOverwrite(send_messages=False),
            roles["coach"]: discord.PermissionOverwrite(send_messages=True),
            roles["oficial"]: discord.PermissionOverwrite(send_messages=True),
        }
    )
    await ch.send("Canal para os **Coaches e Líderes** darem *feedback* geral para o time após as lutas.\n\n(Apenas Coaches/Líderes podem escrever aqui).")

    await cat.create_text_channel("🛡️ | vods-tank")
    await cat.create_text_channel("💚 | vods-healer")
    await cat.create_text_channel("💥 | vods-dps")
    await cat.create_text_channel("✨ | vods-suporte")
    await cat.create_voice_channel("📺 Sala de Análise 1")
    await cat.create_voice_channel("📺 Sala de Análise 2")

async def setup_financeiro(guild, roles):
    """Cria a Categoria GESTÃO FINANCEIRA"""
    cat = await guild.create_category(
        "💰 CATEGORIA: GESTÃO FINANCEIRA",
        overwrites={
            roles["everyone"]: discord.PermissionOverwrite(read_messages=False),
            roles["mercenario"]: discord.PermissionOverwrite(read_messages=True),
            roles["oficial"]: discord.PermissionOverwrite(read_messages=True),
        }
    )
    
    ch = await cat.create_text_channel(
        "ℹ️ | info-regear-e-loot",
        overwrites={ roles["mercenario"]: discord.PermissionOverwrite(send_messages=False) }
    )
    await ch.send("**Regras de Regear e Loot Split**\n\n**Regear:**\n1.  O *core* cobre *regears* (T8.3 equivalente) em CTAs **obrigatórias**.\n2.  Para solicitar, poste o *print* da sua *kill* (morte) no canal #📦 | solicitar-regear.\n3.  Aguarde a aprovação de um Oficial.\n\n**Loot Split:**\n1.  Todo *loot* de ZvZ é recolhido pela liderança.\n2.  Uma taxa de X% é retida para o banco da guilda (regears, *hideout*).\n3.  O restante é dividido igualmente entre os presentes na CTA e pago semanalmente.")

    ch = await cat.create_text_channel("📦 | solicitar-regear")
    await ch.send("Use este canal **apenas** para postar o *screenshot* da sua morte e solicitar o *regear*.\n\nUm Oficial irá reagir com ✅ (Aprovado) ou ❌ (Negado).")
    
    ch = await cat.create_text_channel(
        "🧾 | lootsplit-e-pagamentos",
        overwrites={ roles["mercenario"]: discord.PermissionOverwrite(send_messages=False) }
    )
    await ch.send("Canal para a liderança postar os relatórios de **Loot Split** e confirmar os pagamentos.")

async def setup_admin(guild, roles):
    """Cria a Categoria ADMINISTRAÇÃO (Privada para Oficiais)"""
    cat = await guild.create_category(
        "🔒 CATEGORIA: ADMINISTRAÇÃO",
        overwrites={
            roles["everyone"]: discord.PermissionOverwrite(read_messages=False),
            roles["mercenario"]: discord.PermissionOverwrite(read_messages=False),
            roles["oficial"]: discord.PermissionOverwrite(read_messages=True),
            roles["lider"]: discord.PermissionOverwrite(read_messages=True),
        }
    )
    
    await cat.create_text_channel("💬 | chat-liderança")
    await cat.create_text_channel("📊 | gerenciamento-core")
    await cat.create_text_channel("✅ | regears-aprovados")
    await cat.create_text_channel("🤖 | logs-do-bot")
    await cat.create_voice_channel("🔒 Reunião de Oficiais")


# --- A Classe Cog (Módulo) ---

class SetupCog(commands.Cog):
    """Cog que contém todos os comandos relacionados ao setup do servidor."""
    
    def __init__(self, bot):
        self.bot = bot
        print(">>> setup_cog.py FOI LIDO E INICIADO <<<") # Mensagem de diagnóstico

    @commands.slash_command(
        name="setup-servidor",
        description="Configura este servidor do zero. (Apenas Admins)"
        # Este comando agora é GLOBAL
    )
    @commands.has_permissions(administrator=True)
    async def setup_servidor(self, ctx: discord.ApplicationContext):
        """Comando principal que constrói todo o servidor."""
        
        # Responde ao usuário (apenas ele vê esta mensagem)
        await ctx.respond("Comando `/setup-servidor` recebido! Iniciando a configuração...", ephemeral=True)
        
        guild = ctx.guild
        
        await ctx.channel.send(f"Iniciando a configuração completa do servidor '{guild.name}'...")
        
        # PASSO A: Criar Cargos
        await ctx.channel.send("Criando cargos...")
        roles = await create_roles(guild)
        await ctx.channel.send("✅ Cargos criados.")
        
        # PASSO B-E: Criar Categorias, Canais e Mensagens
        await setup_publico(guild, roles)
        await setup_recepcao(guild, roles)
        await setup_comunidade(guild, roles)
        await setup_zvz(guild, roles)
        await setup_roles_chat(guild, roles)
        await setup_mentoria(guild, roles)
        await setup_financeiro(guild, roles)
        await setup_admin(guild, roles)

        await ctx.channel.send("🚀 **Configuração do Servidor Concluída!** 🚀")

    @setup_servidor.error
    async def setup_servidor_error(self, ctx: discord.ApplicationContext, error):
        """Handler de erro específico para este comando."""
        if isinstance(error, commands.MissingPermissions):
            await ctx.respond("Apenas administradores podem usar este comando.", ephemeral=True)
        else:
            await ctx.respond(f"Ocorreu um erro inesperado: {error}", ephemeral=True)
            print(f"Erro no comando '/setup-servidor': {error}")
            import traceback
            traceback.print_exc()

# Função obrigatória (agora async) que o main.py usa para carregar esta Cog
async def setup(bot):
    await bot.add_cog(SetupCog(bot))

