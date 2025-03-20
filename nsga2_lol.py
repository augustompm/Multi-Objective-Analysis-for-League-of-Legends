import csv
import random
import array
import numpy as np
from deap import algorithms, base, creator, tools

# Configuração inicial do DEAP para NSGA-II
creator.create("FitnessMulti", base.Fitness, weights=(1.0, 1.0))
creator.create("Individual", array.array, typecode='b', fitness=creator.FitnessMulti)

# Parâmetros do NSGA-II (Deb et al., 2002, seção IV)
POP_SIZE = 200
NGEN = 500
CXPB = 0.9
MUTPB = 1 / 169
CHROMOSOME_LENGTH = 169
MAX_POOL_SIZE = 30

# Leitura do CSV dos campeões
champions_data = {}
champion_names = []
with open("champion_performance.csv", newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';')
    for row in reader:
        champion = row["player_champion"]
        champions_data[champion] = {
            "total_matches": int(row["total_matches"].replace(',', '')),
            "total_wins": int(row["total_wins"].replace(',', '')),
            "win_rate": float(row["win_rate"])
        }
        champion_names.append(champion)

# Função de avaliação com penalidade mais forte
def evaluate_individual(individual):
    total_wins = 0
    total_matches = 0
    pool_size = sum(individual)
    
    for i, bit in enumerate(individual):
        if bit == 1:
            champ = champion_names[i]
            total_wins += champions_data[champ]["total_wins"]
            total_matches += champions_data[champ]["total_matches"]
    
    win_rate = total_wins / total_matches if total_matches > 0 else 0.0
    if pool_size > MAX_POOL_SIZE:
        penalty = (pool_size - MAX_POOL_SIZE) * 0.005  # Penalidade aumentada
        win_rate = max(0.0, win_rate - penalty)
    
    return win_rate, pool_size

# Geração de indivíduo com tamanho controlado
def generate_individual():
    ind = creator.Individual([0] * CHROMOSOME_LENGTH)
    target_size = random.randint(1, MAX_POOL_SIZE)
    ones = random.sample(range(CHROMOSOME_LENGTH), target_size)
    for i in ones:
        ind[i] = 1
    return ind

# Configuração da toolbox
toolbox = base.Toolbox()
toolbox.register("individual", generate_individual)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", evaluate_individual)
toolbox.register("mate", tools.cxOnePoint)
toolbox.register("mutate", tools.mutFlipBit, indpb=MUTPB)
toolbox.register("select", tools.selNSGA2)

# Função para remover duplicatas
def remove_duplicates(population):
    unique_dict = {}
    for ind in population:
        ind_tuple = tuple(ind)
        if ind_tuple not in unique_dict:
            unique_dict[ind_tuple] = ind
    return list(unique_dict.values())

# Geração da população inicial
population = toolbox.population(n=POP_SIZE)
population = remove_duplicates(population)

# Avaliar a população inicial
fits = toolbox.map(toolbox.evaluate, population)
for ind, fit in zip(population, fits):
    ind.fitness.values = fit

# Execução do NSGA-II
for gen in range(NGEN):
    offspring = algorithms.varAnd(population, toolbox, CXPB, MUTPB)
    valid_offspring = []
    for ind in offspring:
        if sum(ind) <= MAX_POOL_SIZE:  # Rejeitar pools > 15
            valid_offspring.append(ind)
        else:
            new_ind = toolbox.individual()  # Gerar novo válido
            valid_offspring.append(new_ind)
    
    fits = toolbox.map(toolbox.evaluate, valid_offspring)
    for ind, fit in zip(valid_offspring, fits):
        ind.fitness.values = fit
    
    combined = population + valid_offspring
    combined = remove_duplicates(combined)
    
    while len(combined) < POP_SIZE:
        new_ind = toolbox.individual()
        if tuple(new_ind) not in {tuple(ind) for ind in combined}:
            new_ind.fitness.values = toolbox.evaluate(new_ind)
            combined.append(new_ind)
    
    population = toolbox.select(combined, k=POP_SIZE)

# Extração da frente de Pareto
pareto_front = tools.sortNondominated(population, len(population), first_front_only=True)[0]
pareto_front = remove_duplicates(pareto_front)

# Calcular Crowding Distance
def assign_crowding_distance(front):
    if not front:
        return
    
    for ind in front:
        ind.fitness.crowding_dist = 0.0
    
    for m in range(2):
        valid_front = [ind for ind in front if ind.fitness.valid and len(ind.fitness.values) == 2]
        if len(valid_front) < 2:
            continue
        
        sorted_front = sorted(valid_front, key=lambda x: x.fitness.values[m])
        min_val = min(ind.fitness.values[m] for ind in sorted_front)
        max_val = max(ind.fitness.values[m] for ind in sorted_front)
        if max_val == min_val:
            continue
        
        sorted_front[0].fitness.crowding_dist = float('inf')
        sorted_front[-1].fitness.crowding_dist = float('inf')
        
        for i in range(1, len(sorted_front) - 1):
            sorted_front[i].fitness.crowding_dist += (
                (sorted_front[i+1].fitness.values[m] - sorted_front[i-1].fitness.values[m]) /
                (max_val - min_val)
            )

assign_crowding_distance(pareto_front)

# Ordenar a frente por pool_size (asc) e win_rate (desc)
pareto_front.sort(key=lambda x: (x.fitness.values[1], -x.fitness.values[0]))

# Geração do CSV da frente de Pareto
with open("pareto_front.csv", "w", newline='') as csvfile:
    fieldnames = ["win_rate", "pool_size", "champions", "crowding_distance"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
    writer.writeheader()
    
    for ind in pareto_front:
        if ind.fitness.valid and len(ind.fitness.values) == 2:
            win_rate, pool_size = ind.fitness.values
            selected_champions = [champion_names[i] for i, bit in enumerate(ind) if bit == 1]
            writer.writerow({
                "win_rate": win_rate,
                "pool_size": pool_size,
                "champions": ",".join(selected_champions),
                "crowding_distance": ind.fitness.crowding_dist
            })

num_nondominated = len(pareto_front)
print(f"Número de soluções não-dominadas na frente de Pareto: {num_nondominated}")
print("Frente de Pareto ordenada salva em 'pareto_front.csv'")