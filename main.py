import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import traceback

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
intents.message_content = True  # Habilita leitura do conteúdo das mensagens (necessário para wait_for checks)

# --- 3. Inicialização do Bot ---
# Usamos commands.Bot para carregar Cogs, mas não definimos comandos de prefixo
bot = commands.Bot(command_prefix='!', intents=intents)

# --- 4. Função de Carregamento de Cogs (Dinâmico) ---
async def load_cogs(bot_instance):
    """Carrega dinamicamente todas as Cogs da pasta /cogs."""
    cogs_dir = "cogs"
    print("--- Carregando Módulos (Cogs) ---")
    if not os.path.exists(cogs_dir):
        print(f"AVISO: Diretório '{cogs_dir}' não encontrado. Nenhuma cog será carregada.")
        return

    for filename in os.listdir(cogs_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            try:
                extension = f"{cogs_dir}.{filename[:-3]}"
                await bot_instance.load_extension(extension)
                print(f"  [OK] Módulo '{filename}' carregado.")
            except Exception as e:
                print(f"  [FALHA] Módulo '{filename}': {e}")
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
    # Isto sincroniza os comandos @app_commands.command
    try:
        print("Sincronizando comandos globalmente... (Pode demorar)")
        synced = await bot.tree.sync() 
        print(f"Sincronização global enviada! {len(synced)} comandos sincronizados.")
    except Exception as e:
        print(f"Falha ao sincronizar comandos globalmente: {e}")
        
    print("------ Bot está 100% pronto! ------")

# --- 6. Executar o Bot ---
if __name__ == "__main__":
    bot.run(TOKEN)