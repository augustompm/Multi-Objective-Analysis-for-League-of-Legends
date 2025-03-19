import pandas as pd
import logging
import os

# Configura o logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='deduplicate_match_ids.log',
    filemode='w'
)

# Função para deduplicar match IDs
def deduplicate_match_ids(input_file="match_ids_br1.csv", output_file="unique_match_ids_br1.csv"):
    """
    Lê um CSV com matchIds, remove duplicatas e salva uma lista única em um novo CSV.
    Args:
        input_file (str): Arquivo CSV de entrada com matchIds possivelmente duplicados.
        output_file (str): Arquivo CSV de saída com matchIds únicos.
    """
    try:
        # Lê o CSV de entrada
        df = pd.read_csv(input_file)
        logging.info(f"Carregados {len(df)} matchIds de {input_file}")
        print(f"Carregados {len(df)} matchIds de {input_file}")

        # Remove duplicatas
        unique_df = df.drop_duplicates(subset=["matchId"])
        unique_match_ids = unique_df["matchId"].tolist()
        logging.info(f"Encontrados {len(unique_match_ids)} matchIds únicos após deduplicação")
        print(f"Encontrados {len(unique_match_ids)} matchIds únicos após deduplicação")

        # Salva o resultado em um novo CSV
        unique_df.to_csv(output_file, index=False)
        logging.info(f"Salvou {len(unique_match_ids)} matchIds únicos em {output_file}")
        print(f"Salvou {len(unique_match_ids)} matchIds únicos em {output_file}")

    except FileNotFoundError:
        logging.error(f"Arquivo {input_file} não encontrado")
        print(f"Erro: {input_file} não encontrado")
    except Exception as e:
        logging.error(f"Erro ao processar o arquivo: {e}")
        print(f"Erro inesperado: {e}")

# Main
def main():
    # Configuração dos arquivos
    input_file = "match_ids_br1.csv"
    output_file = "unique_match_ids_br1.csv"

    # Remove o arquivo de saída se já existir
    if os.path.exists(output_file):
        os.remove(output_file)
        logging.info(f"Arquivo {output_file} removido para nova deduplicação")

    # Executa a deduplicação
    deduplicate_match_ids(input_file, output_file)

if __name__ == "__main__":
    main()