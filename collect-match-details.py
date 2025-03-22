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
    filename='collect_match_details.log',
    filemode='w'
)

# Lê a chave da API do arquivo .key
config = configparser.ConfigParser()
config.read(".key")
api_key = config["API"]["api_key"]

# Configuração da API
watcher = LolWatcher(api_key)
platform = "americas"  # Para match.by_id
region = "br1"  # Para champion_mastery.by_summoner_by_champion

# Função para mapear lane e role para position
def map_to_position(lane, role):
    """
    Converte lane e role em uma posição derivada com base nas regras fornecidas.
    """
    mapping = {
        ("MID", "SOLO"): "MIDDLE",
        ("TOP", "SOLO"): "TOP",
        ("JUNGLE", "NONE"): "JUNGLE",
        ("BOT", "DUO_CARRY"): "BOTTOM",
        ("BOT", "DUO_SUPPORT"): "UTILITY"
    }
    return mapping.get((lane, role), "NONE") 

# Função para salvar SQL incrementalmente em matches2
def save_sql_incrementally(match_data, output_file="matches2.sql"):
    """
    Salva os detalhes das partidas em um arquivo SQL com INSERTs para matches2.
    Inclui championPoints como nova coluna.
    """
    with open(output_file, "a") as sql_file:
        for match in match_data:
            sql = (
                f"INSERT INTO matches2 (match_id, player_summoner_id, player_champion, player_won, player_team, "
                f"player_lane, player_role, player_position, game_duration, game_mode, game_start_timestamp, team1_won, "
                f"player_kills, player_deaths, player_assists, champion_points, "
                f"team1_champion1, team1_champion2, team1_champion3, team1_champion4, team1_champion5, "
                f"team2_champion1, team2_champion2, team2_champion3, team2_champion4, team2_champion5) "
                f"VALUES ('{match['matchId']}', '{match['playerSummonerId']}', '{match['playerChampion']}', "
                f"{match['playerWon']}, '{match['playerTeam']}', '{match['playerLane']}', '{match['playerRole']}', "
                f"'{match['playerPosition']}', {match['gameDuration']}, '{match['gameMode']}', {match['gameStartTimestamp']}, "
                f"{match['team1Won']}, {match['playerKills']}, {match['playerDeaths']}, {match['playerAssists']}, "
                f"{match['championPoints']}, "
                f"'{match['team1Champions'][0]}', '{match['team1Champions'][1]}', '{match['team1Champions'][2]}', "
                f"'{match['team1Champions'][3]}', '{match['team1Champions'][4]}', "
                f"'{match['team2Champions'][0]}', '{match['team2Champions'][1]}', '{match['team2Champions'][2]}', "
                f"'{match['team2Champions'][3]}', '{match['team2Champions'][4]}');\n"
            )
            sql_file.write(sql)
    logging.info(f"Salvou {len(match_data)} INSERTs em {output_file}")
    print(f"Salvou {len(match_data)} partidas em {output_file}")

# Função para coletar detalhes das partidas com maestria
def get_match_details(match_ids, summoner_ids):
    """
    Coleta detalhes das partidas, incluindo championPoints, gerando uma linha por jogador Diamante presente.
    """
    match_data = []
    request_count = 0
    total_matches = len(match_ids)
    
    logging.info(f"Iniciando coleta de detalhes para {total_matches} partidas")
    print(f"Total de partidas a processar: {total_matches}")
    
    for i, match_id in enumerate(match_ids):
        try:
            # Busca detalhes da partida
            match = watcher.match.by_id(platform, match_id)
            info = match["info"]
            
            # Pausa para limite de taxa (1 requisição por partida)
            time.sleep(1.125)
            
            # Determina se o time 1 (ID 100) venceu
            team1_won = 1 if info["teams"][0]["win"] else 0
            
            # Separa campeões por time
            team1_champions = []
            team2_champions = []
            our_players = []  # Lista para armazenar nossos jogadores Diamante
            
            # Processa os participantes
            for participant in info["participants"]:
                summoner_id = participant["summonerId"]
                champion = participant["championName"]
                champion_id = participant["championId"]
                
                if participant["teamId"] == 100:
                    team1_champions.append(champion)
                else:  # teamId == 200
                    team2_champions.append(champion)
                
                # Verifica se o participante é um dos nossos jogadores Diamante
                if summoner_id in summoner_ids:
                    # Busca pontos de maestria para esse jogador e campeão
                    mastery = watcher.champion_mastery.by_summoner_by_champion(
                        region, summoner_id, champion_id
                    )
                    champion_points = mastery["championPoints"]
                    
                    # Pausa adicional para requisição de maestria
                    time.sleep(1.125)
                    request_count += 1
                    
                    our_players.append({
                        "summonerId": summoner_id,
                        "champion": champion,
                        "championId": champion_id,
                        "won": 1 if participant["win"] else 0,
                        "team": "team1" if participant["teamId"] == 100 else "team2",
                        "lane": participant["lane"],
                        "role": participant["role"],
                        "kills": participant["kills"],
                        "deaths": participant["deaths"],
                        "assists": participant["assists"],
                        "championPoints": champion_points
                    })
            
            # Preenche com valores padrão se faltar campeões
            while len(team1_champions) < 5:
                team1_champions.append("Unknown")
            while len(team2_champions) < 5:
                team2_champions.append("Unknown")
            
            # Gera uma linha por jogador Diamante encontrado
            for player in our_players:
                match_info = {
                    "matchId": match_id,
                    "playerSummonerId": player["summonerId"],
                    "playerChampion": player["champion"],
                    "playerWon": player["won"],
                    "playerTeam": player["team"],
                    "playerLane": player["lane"],
                    "playerRole": player["role"],
                    "playerPosition": map_to_position(player["lane"], player["role"]),
                    "gameDuration": info["gameDuration"],
                    "gameMode": info["gameMode"],
                    "gameStartTimestamp": info["gameStartTimestamp"],
                    "team1Won": team1_won,
                    "playerKills": player["kills"],
                    "playerDeaths": player["deaths"],
                    "playerAssists": player["assists"],
                    "championPoints": player["championPoints"],
                    "team1Champions": team1_champions,
                    "team2Champions": team2_champions
                }
                match_data.append(match_info)
            
            request_count += 1
            logging.info(f"Partida {match_id} ({i+1}/{total_matches}): {len(our_players)} jogadores Diamante encontrados")
            print(f"[{i+1}/{total_matches}] Detalhes coletados para {match_id} ({len(our_players)} jogadores Diamante)")
            
            # Controle de taxa da API e salvamento incremental
            if request_count % 20 == 0:
                logging.debug(f"Limite de 20 requisições atingido. Pausando por 1,5s...")
                time.sleep(1.5)  # Mantido para evitar erro 429
                save_sql_incrementally(match_data)
                match_data = []
            
        except Exception as e:
            logging.error(f"Erro ao processar {match_id}: {e}")
            print(f"Erro em {match_id}: {e}")
            continue
    
    # Salvamento final
    if match_data:
        save_sql_incrementally(match_data)
    
    logging.info(f"Coleta concluída. Total de requisições: {request_count}")
    print(f"Finalizado: {request_count} requisições processadas")

# Main
def main():
    try:
        # Carrega os summonerIds do CSV original para rastrear nossos jogadores
        players_df = pd.read_csv("diamond_players_br1.csv")
        summoner_ids = set(players_df["summonerId"])
        logging.info(f"Carregados {len(summoner_ids)} summonerIds de diamond_players_br1.csv")
        
        # Lê os matchIds do CSV parcial
        match_ids_df = pd.read_csv("match_ids_br1.csv")
        match_ids = match_ids_df["matchId"].tolist()
        
        logging.info(f"Carregados {len(match_ids)} matchIds para processamento")
        print(f"Carregados {len(match_ids)} matchIds")
        
        # Remove o arquivo SQL existente
        output_file = "matches2.sql"
        if os.path.exists(output_file):
            os.remove(output_file)
            logging.info(f"Arquivo {output_file} removido para nova coleta")
        
        get_match_details(match_ids, summoner_ids)
        
    except FileNotFoundError as e:
        logging.error(f"Arquivo não encontrado: {e}")
        print(f"Erro: {e}")
    except Exception as e:
        logging.error(f"Erro geral no script: {e}")
        print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    main()