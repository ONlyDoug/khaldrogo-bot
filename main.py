import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# --- 1. Carregamento do Token ---
# (load_dotenv() é útil se ainda quiseres testar no teu PC, mas a Discloud irá ignorá-lo)
load_dotenv() 
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print("ERRO CRÍTICO: 'DISCORD_TOKEN' não foi encontrado nas variáveis de ambiente.")
    exit()

# --- 2. Definição das "Intents" (Intenções) ---
intents = discord.Intents.default()
intents.guilds = True
intents.members = True

# --- 3. Inicialização do Bot ---
bot = commands.Bot(command_prefix='.', intents=intents)

# --- 4. Comando de Diagnóstico (Global) ---
@bot.slash_command(
    name="ping",
    description="Testa se o bot está vivo e a sincronizar comandos."
    # Sem 'guild_id', este comando torna-se GLOBAL
)
async def ping(ctx: discord.ApplicationContext):
    """Responde 'Pong!' para teste."""
    await ctx.respond("Pong! O bot está a funcionar.", ephemeral=True)


# --- 5. Evento de Inicialização (On Ready) ---
@bot.event
async def on_ready():
    """Chamado quando o bot está pronto e online."""
    print(f'Bot logado como {bot.user}')
    
    try:
        await bot.load_extension("cogs.setup_cog")
        print("Módulo (Cog) 'setup_cog' carregado com sucesso.")
    except Exception as e:
        print(f"Falha ao carregar a cog 'setup_cog': {e}")
        return

    # --- Sincronização GLOBAL (para Discloud) ---
    try:
        print("Sincronizando comandos globalmente... (Pode demorar até 1 hora)")
        # Sincroniza globalmente.
        await bot.tree.sync() 
        print("Sincronização global enviada!")
    except Exception as e:
        print(f"Falha ao sincronizar comandos globalmente: {e}")
        
    print("------ Bot está 100% pronto! ------")

# --- 6. Executar o Bot ---
bot.run(TOKEN)

