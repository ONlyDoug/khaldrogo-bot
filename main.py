import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

# --- 1. Carregamento do Token ---
load_dotenv() 
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print("ERRO CRÍTICO: 'DISCORD_TOKEN' não foi encontrado nas variáveis de ambiente.")
    exit()

# --- 2. Definição das "Intents" (Intenções) ---
intents = discord.Intents.default()
intents.guilds = True    # Necessário para gerir cargos/canais
intents.members = True   # Necessário para gerir membros

# --- 3. Inicialização do Bot ---
bot = commands.Bot(command_prefix='.', intents=intents)

# --- 4. Comando de Diagnóstico (Global) ---
@bot.slash_command(
    name="ping",
    description="Testa se o bot está vivo e a sincronizar comandos."
)
async def ping(ctx: discord.ApplicationContext):
    """Responde 'Pong!' para teste."""
    await ctx.respond(f"Pong! Latência: {round(bot.latency * 1000)}ms", ephemeral=True)


async def load_cogs(bot_instance):
    """Carrega dinamicamente todas as Cogs da pasta /cogs."""
    cogs_dir = "cogs"
    print("--- Carregando Módulos (Cogs) ---")
    if not os.path.exists(cogs_dir):
        print(f"AVISO: Diretório '{cogs_dir}' não encontrado. Nenhuma cog será carregada.")
        return

    for filename in os.listdir(cogs_dir):
        # Carrega apenas ficheiros .py que não sejam de inicialização
        if filename.endswith(".py") and not filename.startswith("__"):
            try:
                # Converte 'nome_ficheiro.py' para 'cogs.nome_ficheiro'
                extension = f"{cogs_dir}.{filename[:-3]}"
                await bot_instance.load_extension(extension)
                print(f"  [OK] Módulo '{filename}' carregado.")
            except Exception as e:
                print(f"  [FALHA] Módulo '{filename}': {e}")
                import traceback
                traceback.print_exc()
    print("-----------------------------------")


# --- 5. Evento de Inicialização (On Ready) ---
@bot.event
async def on_ready():
    """Chamado quando o bot está pronto e online."""
    print(f'Bot logado como {bot.user}')
    
    # Carrega as Cogs dinamicamente
    await load_cogs(bot)

    # --- Sincronização GLOBAL (para Discloud) ---
    try:
        print("Sincronizando comandos globalmente... (Pode demorar)")
        await bot.tree.sync() 
        print("Sincronização global enviada!")
    except Exception as e:
        print(f"Falha ao sincronizar comandos globalmente: {e}")
        
    print("------ Bot está 100% pronto! ------")

# --- 6. Executar o Bot ---
if __name__ == "__main__":
    bot.run(TOKEN)

