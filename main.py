import discord
from discord.ext import commands
import os
import asyncio
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

# Função para carregar dinamicamente todas as cogs em /cogs
async def load_cogs(bot):
    """Carrega dinamicamente todas as Cogs da pasta /cogs."""
    cogs_dir = "cogs"
    print("--- Carregando Módulos (Cogs) ---")
    if not os.path.isdir(cogs_dir):
        print(f"  [AVISO] Pasta '{cogs_dir}' não encontrada. Nenhuma cog carregada.")
        print("-----------------------------------")
        return

    for filename in os.listdir(cogs_dir):
        # Carrega apenas ficheiros .py que não sejam de inicialização
        if filename.endswith(".py") and not filename.startswith("__"):
            try:
                # Converte 'nome_ficheiro.py' para 'cogs.nome_ficheiro'
                extension = f"{cogs_dir}.{filename[:-3]}"
                await bot.load_extension(extension)
                print(f"  [OK] Módulo '{filename}' carregado.")
            except Exception as e:
                print(f"  [FALHA] Módulo '{filename}': {e}")
    print("-----------------------------------")

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
    
    # Carrega todas as cogs dinamicamente
    await load_cogs(bot)

    # --- Sincronização GLOBAL (para Discloud) ---
    try:
        print("Sincronizando comandos globalmente...")
        await bot.tree.sync() 
        print("Sincronização global enviada!")
    except Exception as e:
        print(f"Falha ao sincronizar comandos globalmente: {e}")
        
    print("------ Bot está 100% pronto! ------")

# --- 6. Executar o Bot ---
bot.run(TOKEN)

