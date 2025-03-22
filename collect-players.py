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
    filemode='w'  # 'a' para append se quiser histórico
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
    players = []
    request_count = 0
    divisions = ["I", "II", "III", "IV"]
    target_per_division = 2500  # 10.000 / 4 divisões
    max_pages = 13  # 13 páginas × ~205 jogadores = ~2.665 por divisão, suficiente para 2.500
    
    for div in divisions:
        page = 1
        division_players = []
        while len(division_players) < target_per_division and page <= max_pages:
            retries = 3
            while retries > 0:
                try:
                    response = watcher.league.entries(region, "RANKED_SOLO_5x5", "DIAMOND", div, page=page)
                    if response:
                        division_players.extend(response)
                        logging.info(f"Coletados {len(response)} jogadores da divisão DIAMOND {div}, página {page}")
                        print(f"Coletados {len(response)} jogadores da divisão DIAMOND {div}, página {page}")
                    else:
                        logging.warning(f"Nenhum jogador retornado para DIAMOND {div}, página {page}")
                        print(f"Nenhum jogador retornado para DIAMOND {div}, página {page}")
                        break
                    
                    request_count += 1
                    if request_count % 20 == 0:
                        time.sleep(1.2)  # 20 req/s
                    if request_count % 100 == 0:
                        time.sleep(120)  # 100 req/2 min
                    break  # Sai do retry se sucesso
                except Exception as e:
                    logging.error(f"Erro ao coletar DIAMOND {div}, página {page}: {e}")
                    print(f"Erro ao coletar DIAMOND {div}, página {page}: {e}")
                    retries -= 1
                    if retries > 0:
                        time.sleep(10)  # Espera antes de retry
                    else:
                        logging.error(f"Falha após retries em DIAMOND {div}, página {page}")
                        break
            page += 1
        
        players.extend(division_players[:target_per_division])
        logging.info(f"Total coletado para DIAMOND {div}: {len(division_players[:target_per_division])}")
        print(f"Total coletado para DIAMOND {div}: {len(division_players[:target_per_division])}")
    
    total_players = len(players[:10000])
    logging.info(f"Total de jogadores coletados: {total_players}")
    print(f"Total de jogadores coletados: {total_players}")
    return players[:10000]

# Main
def main():
    diamond_players = get_diamond_players()
    df_players = pd.DataFrame(diamond_players)
    df_players.to_csv("diamond_players_br1.csv", index=False)
    logging.info(f"Dados salvos em diamond_players_br1.csv com {len(diamond_players)} jogadores")
    print(f"Dados salvos em diamond_players_br1.csv com {len(diamond_players)} jogadores")

if __name__ == "__main__":
    main()