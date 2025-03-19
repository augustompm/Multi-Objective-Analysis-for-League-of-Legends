# Multi-Objective-Analysis-for-League-of-Legends 

This project applies multi-objective optimization to analyze the trade-off between champion diversity and win rate in League of Legends, targeting 1000 Diamond-tier players in the S2024 S3 season. 

## Overview The pipeline consists of three Python scripts to collect and process data from the Riot Games API: 
1. **Collect Players**: Gathers Diamond-tier player data. 
2. **Collect Match IDs**: Retrieves ranked solo/duo match IDs. 
3. **Collect Match Details**: Extracts detailed match data for analysis. 

## Prerequisites 
- Python 3.x 
- Libraries: `pandas`, `riotwatcher` 
- Riot API key (stored in a `.key` file with `[API]\napi_key=your_key_here`) 

## Scripts 

### 1. `collect-players.py` 
- **Purpose**: Collects 1,000 Diamond-tier players from the `br1` server. 
- **Output**: `diamond_players_br1.csv` (player data). 
- **Run**: ```bash python3 collect-players.py ``` 

### 2. `collect-match-ids.py` 
- **Purpose**: Fetches ranked solo/duo match IDs (queue 420) for players from `diamond_players_br1.csv` in S2024 S3 (09/24/2024 - 01/08/2025). 
- **Output**: `match_ids_br1.csv` (match IDs). 
- **Run**: ```bash python3 collect-match-ids.py ``` 

### 3. `collect-match-details.py` 

- **Purpose**: Retrieves detailed match data (champions, win/loss, lane, role, etc.) for matches in `match_ids_br1.csv`. 
- **Output**: `matches.sql` (SQL INSERT statements). 
- **Run**: ```bash python3 collect-match-details.py ``` 

## Usage 

1. Set up your Riot API key in `.key`. 
2. Run scripts sequentially: ```bash python3 collect-players.py python3 collect-match-ids.py python3 collect-match-details.py ``` 
3. Import `matches.sql` into a MySQL database for analysis. 

## Notes - Scripts include rate limiting to respect Riot API constraints. 

- Data is stored in CSV and SQL formats for flexibility. 

## Done by Augusto Mendonça, Filipe Sousa & Guilherme Garcia