import pandas as pd
from riotwatcher import LolWatcher
import time
import logging
import os
import configparser
import sys

# Configura o logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='collect_match_details.log',
    filemode='w'
)

# Lê a chave da API
config = configparser.ConfigParser()
config.read(".key")
api_key = config["API"]["api_key"]

# Configuração da API
watcher = LolWatcher(api_key)
platform = "americas"
region = "br1"

# Função para mapear lane e role para position
def map_to_position(lane, role):
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
    with open(output_file, "a") as sql_file:
        for match in match_data:
            sql = (
                f"INSERT INTO matches2 (match_id, player_summoner_id, player_puuid, player_champion, player_won, player_team, "
                f"player_lane, player_role, player_position, game_duration, game_mode, game_start_timestamp, team1_won, "
                f"player_kills, player_deaths, player_assists, champion_points, "
                f"team1_champion1, team1_champion2, team1_champion3, team1_champion4, team1_champion5, "
                f"team2_champion1, team2_champion2, team2_champion3, team2_champion4, team2_champion5) "
                f"VALUES ('{match['matchId']}', '{match['playerSummonerId']}', '{match['playerPUUID']}', '{match['playerChampion']}', "
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

# Função para coletar detalhes das partidas com maestria e timer
def get_match_details(match_ids, summoner_data):
    match_data = []
    request_count = 0
    total_matches = len(match_ids)
    
    summoner_map = dict(zip(summoner_data["summonerId"], summoner_data["puuid"]))
    summoner_ids = set(summoner_map.keys())
    
    logging.info(f"Iniciando coleta de detalhes para {total_matches} partidas")
    print(f"Total de partidas a processar: {total_matches}")
    
    for i, match_id in enumerate(match_ids):
        start_time = time.time()
        try:
            match = watcher.match.by_id(platform, match_id)
            info = match["info"]
            
            time.sleep(0.3)
            
            team1_won = 1 if info["teams"][0]["win"] else 0
            
            team1_champions = []
            team2_champions = []
            our_players = []
            
            for participant in info["participants"]:
                summoner_id = participant["summonerId"]
                champion = participant["championName"]
                champion_id = participant["championId"]
                
                if participant["teamId"] == 100:
                    team1_champions.append(champion)
                else:
                    team2_champions.append(champion)
                
                if summoner_id in summoner_ids:
                    puuid = summoner_map.get(summoner_id)
                    if not puuid:
                        logging.warning(f"PUUID não encontrado para summonerId {summoner_id}")
                        continue
                    
                    retries = 3
                    champion_points = -9999  # Fallback para erro
                    while retries > 0:
                        try:
                            mastery = watcher.champion_mastery.by_puuid_by_champion(
                                region, puuid, champion_id
                            )
                            champion_points = mastery["championPoints"]
                            logging.info(f"Maestria coletada para PUUID {puuid}, champion {champion}: {champion_points}")
                            break
                        except Exception as e:
                            logging.warning(f"Erro ao buscar maestria para PUUID {puuid}, champion {champion_id}: {str(e)}")
                            retries -= 1
                            if retries > 0:
                                time.sleep(2)
                            else:
                                logging.error(f"Falha após retries para maestria de {puuid}, champion {champion_id}: {str(e)}")
                                champion_points = -9999
                    
                    time.sleep(0.2)
                    request_count += 1
                    
                    our_players.append({
                        "summonerId": summoner_id,
                        "puuid": puuid,
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
            
            while len(team1_champions) < 5:
                team1_champions.append("Unknown")
            while len(team2_champions) < 5:
                team2_champions.append("Unknown")
            
            for player in our_players:
                match_info = {
                    "matchId": match_id,
                    "playerSummonerId": player["summonerId"],
                    "playerPUUID": player["puuid"],
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
            end_time = time.time()
            execution_time = end_time - start_time
            logging.info(f"Partida {match_id} ({i+1}/{total_matches}): {len(our_players)} jogadores Diamante encontrados, tempo: {execution_time:.2f}s")
            print(f"[{i+1}/{total_matches}] Detalhes coletados para {match_id} ({len(our_players)} jogadores Diamante) em {execution_time:.2f}s")
            
            if len(match_data) >= 10:
                logging.debug(f"Salvando {len(match_data)} linhas...")
                save_sql_incrementally(match_data)
                match_data = []
            if request_count % 100 == 0:
                logging.debug(f"Limite de 100 requisições atingido. Pausando por 10s...")
                time.sleep(1)
            
        except Exception as e:
            logging.error(f"Erro ao processar {match_id}: {str(e)}")
            print(f"Erro em {match_id}: {str(e)}")
            time.sleep(1)
    
    if match_data:
        save_sql_incrementally(match_data)
    
    logging.info(f"Coleta concluída. Total de requisições: {request_count}")
    print(f"Finalizado: {request_count} requisições processadas")

# Main
def main():
    try:
        players_df = pd.read_csv("diamond_players_br1.csv")
        logging.info(f"Carregados {len(players_df)} summonerIds de diamond_players_br1.csv")
        print(f"Carregados {len(players_df)} summonerIds de diamond_players_br1.csv")
        
        match_ids_df = pd.read_csv("match_ids_br1.csv")
        if "matchId" not in match_ids_df.columns:
            raise ValueError("Coluna 'matchId' não encontrada em match_ids_br1.csv")
        match_ids = match_ids_df["matchId"].tolist()
        
        logging.info(f"Carregados {len(match_ids)} matchIds para processamento")
        print(f"Carregados {len(match_ids)} matchIds")
        
        output_file = "matches2.sql"
        if os.path.exists(output_file):
            os.remove(output_file)
            logging.info(f"Arquivo {output_file} removido para nova coleta")
            print(f"Arquivo {output_file} removido para nova coleta")
        
        get_match_details(match_ids, players_df)
        
    except FileNotFoundError as e:
        logging.error(f"Arquivo não encontrado: {e}")
        print(f"Erro: {e}")
    except ValueError as e:
        logging.error(f"Erro de valor: {e}")
        print(f"Erro: {e}")
    except Exception as e:
        logging.error(f"Erro geral no script: {str(e)}")
        print(f"Erro inesperado: {str(e)}")

if __name__ == "__main__":
    main()