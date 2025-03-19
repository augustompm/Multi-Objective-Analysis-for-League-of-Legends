import pandas as pd
from riotwatcher import LolWatcher
import time
import logging
import os
import configparser

# Configura o logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='collect_match_ids.log',
    filemode='w'
)

# Lê a chave da API do arquivo .key
config = configparser.ConfigParser()
config.read(".key")
api_key = config["API"]["api_key"]

# Configuração da API
watcher = LolWatcher(api_key)
region = "br1"
platform = "americas"
start_time = 1704891600
end_time = 1715731200    

# Função para salvar match IDs
def save_match_ids(match_ids, output_file="match_ids_br1.csv", mode='w'):
    """
    Salva os match IDs em um arquivo CSV, com opção de sobrescrever ou adicionar.
    """
    df = pd.DataFrame(list(match_ids), columns=["matchId"])
    df.to_csv(output_file, mode=mode, header=not os.path.exists(output_file) if mode == 'a' else True, index=False)
    logging.info(f"Salvou {len(match_ids)} match IDs em {output_file} (mode={mode})")

# Função para coletar match IDs dos jogadores
def get_match_ids(players_df):
    """
    Coleta match IDs de partidas ranqueadas solo (queue=420) para cada jogador.
    """
    match_ids = set()  
    request_count = 0
    total_players = len(players_df)
    
    # Carrega matchIds existentes, se houver
    output_file = "match_ids_br1.csv"
    if os.path.exists(output_file):
        existing_df = pd.read_csv(output_file)
        match_ids.update(existing_df["matchId"].tolist())
        logging.info(f"Carregados {len(match_ids)} matchIds existentes de {output_file}")
    
    logging.info(f"Iniciando coleta de match IDs para {total_players} jogadores")
    print(f"Total de jogadores a processar: {total_players}")
    
    for index, row in players_df.iterrows():
        summoner_id = row["summonerId"]
        try:
            summoner = watcher.summoner.by_id(region, summoner_id)
            puuid = summoner["puuid"]
            request_count += 1
            
            matches = watcher.match.matchlist_by_puuid(
                platform, puuid, start_time=start_time, end_time=end_time, queue=420
            )
            new_matches = len(matches) - len(match_ids.intersection(matches))
            match_ids.update(matches)
            request_count += 1
            
            logging.info(f"Summoner {summoner_id} ({index+1}/{total_players}): {len(matches)} partidas coletadas ({new_matches} novas)")
            print(f"[{index+1}/{total_players}] Coletados {len(matches)} match IDs ({new_matches} novas) para {summoner_id}")
            
            if request_count % 20 == 0:
                time.sleep(1.2)
                save_match_ids(match_ids, "temp_match_ids.csv", mode='w')  
                print(f"Checkpoint: {len(match_ids)} match IDs salvos temporariamente")
            
            if request_count % 100 == 0:
                print(f"Pausa de 2 minutos após {request_count} requisições...")
                time.sleep(120)
            
        except Exception as e:
            logging.error(f"Erro ao processar {summoner_id}: {e}")
            print(f"Erro em {summoner_id}: {e}")
            continue
    
    # Salvamento final com unicidade
    save_match_ids(match_ids, output_file, mode='w')  # Sobrescreve o arquivo final
    if os.path.exists("temp_match_ids.csv"):
        os.remove("temp_match_ids.csv")  # Remove o temporário
    logging.info(f"Coleta concluída. Total de match IDs únicos: {len(match_ids)}")
    print(f"Finalizado: {len(match_ids)} match IDs únicos coletados")
    return match_ids

# Main
def main():
    try:
        players_df = pd.read_csv("diamond_players_br1.csv")
        logging.info("Arquivo diamond_players_br1.csv carregado com sucesso")
        print("Carregando diamond_players_br1.csv...")
        
        get_match_ids(players_df)
        
    except FileNotFoundError:
        logging.error("Arquivo diamond_players_br1.csv não encontrado")
        print("Erro: diamond_players_br1.csv não encontrado")
    except Exception as e:
        logging.error(f"Erro geral no script: {e}")
        print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    main()