import pandas as pd
from riotwatcher import LolWatcher
import time
import logging
import configparser

# Configura o logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='collect_players.log',
    filemode='w'
)

# Lê a chave da API do arquivo .key
config = configparser.ConfigParser()
config.read(".key")
api_key = config["API"]["api_key"]

# Configuração inicial da API
watcher = LolWatcher(api_key)
region = "br1"  # Servidor brasileiro

# Função para coletar jogadores Diamante do Brasil
def get_diamond_players():
    """
    Coleta até 1.000 jogadores Diamante do servidor br1, usando paginação.
    """
    players = []
    request_count = 0
    divisions = ["I", "II", "III", "IV"]
    target_per_division = 250  # 250 por divisão para totalizar 1.000
    
    for div in divisions:
        page = 1
        division_players = []
        while len(division_players) < target_per_division and page <= 2:  # Limita a 2 páginas por divisão
            try:
                response = watcher.league.entries(region, "RANKED_SOLO_5x5", "DIAMOND", div, page=page)
                if response:
                    division_players.extend(response)
                    print(f"Coletados {len(response)} jogadores da divisão DIAMOND {div}, página {page}")
                else:
                    print(f"Nenhum jogador retornado para DIAMOND {div}, página {page}")
                    break
                
                request_count += 1
                if request_count % 20 == 0:
                    time.sleep(1.2)
                if request_count % 100 == 0:
                    time.sleep(120)
                page += 1
            except Exception as e:
                print(f"Erro ao coletar DIAMOND {div}, página {page}: {e}")
                break
        
        players.extend(division_players[:target_per_division])  # Limita a 250 por divisão
    
    total_players = len(players[:1000])  # Limita a 1.000 no total
    return players[:1000]

# Main
def main():
    diamond_players = get_diamond_players()
    if diamond_players is not None:
        df_players = pd.DataFrame(diamond_players)
        df_players.to_csv("diamond_players_br1.csv", index=False)
        logging.info(f"Total de {len(diamond_players)} jogadores Diamante coletados do Brasil")
        print(f"Total de {len(diamond_players)} jogadores Diamante coletados do Brasil")
    else:
        logging.error("Falha na coleta de jogadores")
        print("Falha na coleta de jogadores. Verifique os erros acima.")

if __name__ == "__main__":
    main()