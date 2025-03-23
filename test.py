from riotwatcher import LolWatcher
import time
import configparser

# Lê a chave da API do arquivo .key
config = configparser.ConfigParser()
config.read(".key")
api_key = config["API"]["api_key"]

watcher = LolWatcher(api_key)
region = "br1"
puuid = "3DE58D1PZ7R8GXsPI61VdT4T-e6NNG3Gg4tq-DChUCYBCkUAfnBXp8yvjxH2IQ9pp81JlLzh9pi2Wg"
champion_id = 92

try:
    start_time = time.time()
    mastery = watcher.champion_mastery.by_puuid_by_champion(region, puuid, champion_id)
    print(f"Maestria: {mastery['championPoints']} em {time.time() - start_time:.2f}s")
except Exception as e:
    print(f"Erro: {str(e)}")