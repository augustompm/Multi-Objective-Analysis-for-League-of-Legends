import matplotlib.pyplot as plt

# Dados da frente de Pareto fornecidos
pareto_data = [
    {"win_rate": 0.5864978902953587, "pool_size": 1.0, "champions": "Sivir", "crowding_distance": float('inf')},
    {"win_rate": 0.5838926174496645, "pool_size": 2.0, "champions": "Akshan,Sivir", "crowding_distance": 0.2914889115835343},
    {"win_rate": 0.5802292263610315, "pool_size": 3.0, "champions": "Akshan,Soraka,Sivir", "crowding_distance": 0.234559665550785},
    {"win_rate": 0.5792276964047937, "pool_size": 4.0, "champions": "Kled,Akshan,Soraka,Sivir", "crowding_distance": 0.1490111372208629},
    {"win_rate": 0.5779742765273312, "pool_size": 5.0, "champions": "Akshan,Fizz,Vladimir,Soraka,Sivir", "crowding_distance": 0.1307737922384733},
    {"win_rate": 0.5774865073245952, "pool_size": 6.0, "champions": "Kled,Akshan,Fizz,Vladimir,Soraka,Sivir", "crowding_distance": 0.11215718655572966},
    {"win_rate": 0.5767575322812052, "pool_size": 7.0, "champions": "Kled,Rammus,Akshan,Fizz,Vladimir,Soraka,Sivir", "crowding_distance": 0.13033867823852247},
    {"win_rate": 0.5757575757575758, "pool_size": 8.0, "champions": "Kled,Rammus,Seraphine,Akshan,Fizz,Vladimir,Soraka,Sivir", "crowding_distance": 0.1236704456921185},
    {"win_rate": 0.5752164502164502, "pool_size": 9.0, "champions": "Taric,Kled,Rammus,Seraphine,Akshan,Fizz,Vladimir,Soraka,Sivir", "crowding_distance": 0.1227499698179351},
    {"win_rate": 0.5742424242424242, "pool_size": 10.0, "champions": "Bard,Taric,Kled,Rammus,Seraphine,Akshan,Fizz,Vladimir,Soraka,Sivir", "crowding_distance": 0.13718579272076015},
    {"win_rate": 0.5732946298984035, "pool_size": 11.0, "champions": "Nilah,Bard,Taric,Kled,Rammus,Seraphine,Akshan,Fizz,Vladimir,Soraka,Sivir", "crowding_distance": 0.15100277948639004},
    {"win_rate": 0.5719313682358117, "pool_size": 12.0, "champions": "Nilah,Yorick,Bard,Taric,Kled,Rammus,Seraphine,Akshan,Fizz,Vladimir,Soraka,Sivir", "crowding_distance": 0.14616855549617588},
    {"win_rate": 0.5711197578901859, "pool_size": 13.0, "champions": "Chogath,Nilah,Zilean,Bard,Taric,Kled,Rammus,Seraphine,Akshan,Fizz,Vladimir,Soraka,Sivir", "crowding_distance": 0.13472962467524435},
    {"win_rate": 0.5700787401574803, "pool_size": 14.0, "champions": "Chogath,Nilah,Zilean,Ivern,Bard,Taric,Kled,Rammus,Seraphine,Akshan,Fizz,Vladimir,Soraka,Sivir", "crowding_distance": 0.1402475823722641},
    {"win_rate": 0.5691116844821231, "pool_size": 15.0, "champions": "Chogath,Nilah,Zilean,Nasus,Ivern,Bard,Taric,Kled,Rammus,Seraphine,Akshan,Fizz,Vladimir,Soraka,Sivir", "crowding_distance": 0.12883445588259843},
    {"win_rate": 0.5683921837504285, "pool_size": 16.0, "champions": "Chogath,Nilah,Zilean,KogMaw,Yorick,Ivern,Bard,Taric,Kled,Rammus,Seraphine,Akshan,Fizz,Vladimir,Soraka,Sivir", "crowding_distance": 0.11992397993356713},
    {"win_rate": 0.5676761433868974, "pool_size": 17.0, "champions": "Chogath,Nilah,Zilean,KogMaw,Yorick,Ivern,Bard,Riven,Taric,Kled,Rammus,Seraphine,Akshan,Fizz,Vladimir,Soraka,Sivir", "crowding_distance": 0.11737483631055923},
    {"win_rate": 0.5670284540921091, "pool_size": 18.0, "champions": "Chogath,Nilah,Zilean,Nasus,KogMaw,Yorick,Ivern,Bard,Riven,Taric,Kled,Rammus,Seraphine,Akshan,Fizz,Vladimir,Soraka,Sivir", "crowding_distance": 0.11484099305362305},
    {"win_rate": 0.5663837941418013, "pool_size": 19.0, "champions": "Chogath,Nilah,Zilean,Nasus,KogMaw,Pantheon,Yorick,Ivern,Bard,Riven,Taric,Kled,Rammus,Seraphine,Akshan,Fizz,Vladimir,Soraka,Sivir", "crowding_distance": 0.11221173945617477},
    {"win_rate": 0.5658101730466701, "pool_size": 20.0, "champions": "Chogath,Nilah,Malzahar,Zilean,Nasus,KogMaw,Pantheon,Yorick,Ivern,Bard,Riven,Taric,Kled,Rammus,Seraphine,Akshan,Fizz,Vladimir,Soraka,Sivir", "crowding_distance": 0.1111397540290821},
    {"win_rate": 0.5651957117925704, "pool_size": 21.0, "champions": "Chogath,Nilah,Malzahar,MasterYi,Zilean,Nasus,KogMaw,Pantheon,Yorick,Ivern,Bard,Riven,Taric,Kled,Rammus,Seraphine,Akshan,Fizz,Vladimir,Soraka,Sivir", "crowding_distance": 0.10956306538207101},
    {"win_rate": 0.5646665072914177, "pool_size": 22.0, "champions": "Chogath,Nilah,Trundle,Malzahar,MasterYi,Zilean,Nasus,KogMaw,Pantheon,Yorick,Ivern,Bard,Riven,Taric,Kled,Rammus,Seraphine,Akshan,Fizz,Vladimir,Soraka,Sivir", "crowding_distance": 0.108202700753304},
    {"win_rate": 0.564090368608799, "pool_size": 23.0, "champions": "Heimerdinger,Chogath,Nilah,Trundle,Malzahar,MasterYi,Zilean,Nasus,KogMaw,Pantheon,Yorick,Ivern,Bard,Riven,Taric,Kled,Rammus,Seraphine,Akshan,Fizz,Vladimir,Soraka,Sivir", "crowding_distance": 0.1102789745245405},
    {"win_rate": 0.5635026737967914, "pool_size": 24.0, "champions": "Heimerdinger,Chogath,Nilah,Trundle,Malzahar,MasterYi,Zilean,TahmKench,Nasus,KogMaw,Pantheon,Yorick,Ivern,Bard,Riven,Taric,Kled,Rammus,Seraphine,Akshan,Fizz,Vladimir,Soraka,Sivir", "crowding_distance": 0.11172780578905112},
    {"win_rate": 0.5628857203660353, "pool_size": 25.0, "champions": "Heimerdinger,XinZhao,Chogath,Nilah,Trundle,Malzahar,MasterYi,Zilean,TahmKench,Nasus,KogMaw,Pantheon,Yorick,Ivern,Bard,Riven,Taric,Kled,Rammus,Seraphine,Akshan,Fizz,Vladimir,Soraka,Sivir", "crowding_distance": 0.1225282087435357},
    {"win_rate": 0.561993769470405, "pool_size": 26.0, "champions": "Heimerdinger,Quinn,XinZhao,Chogath,Nilah,Trundle,Malzahar,MasterYi,Zilean,TahmKench,Nasus,KogMaw,Pantheon,Yorick,Ivern,Bard,Riven,Taric,Kled,Rammus,Seraphine,Akshan,Fizz,Vladimir,Soraka,Sivir", "crowding_distance": 0.06465531285838394},
    {"win_rate": 0.561993769470405, "pool_size": 26.0, "champions": "Heimerdinger,Hecarim,XinZhao,Chogath,Nilah,Trundle,Malzahar,MasterYi,Zilean,TahmKench,Nasus,KogMaw,Pantheon,Yorick,Ivern,Bard,Riven,Taric,Kled,Rammus,Seraphine,Akshan,Fizz,Vladimir,Soraka,Sivir", "crowding_distance": 0.06614499844747435},
    {"win_rate": 0.5611437842222673, "pool_size": 27.0, "champions": "Heimerdinger,Hecarim,Quinn,XinZhao,Chogath,Nilah,Trundle,Malzahar,MasterYi,Zilean,TahmKench,Nasus,KogMaw,Pantheon,Yorick,Ivern,Bard,Riven,Taric,Kled,Rammus,Seraphine,Akshan,Fizz,Vladimir,Soraka,Sivir", "crowding_distance": 0.1303740413840913},
    {"win_rate": 0.560263841694983, "pool_size": 28.0, "champions": "Heimerdinger,Kennen,Hecarim,Quinn,XinZhao,Chogath,Nilah,Trundle,Malzahar,MasterYi,Zilean,TahmKench,Nasus,KogMaw,Pantheon,Yorick,Ivern,Bard,Riven,Taric,Kled,Rammus,Seraphine,Akshan,Fizz,Vladimir,Soraka,Sivir", "crowding_distance": 0.13398225326157454},
    {"win_rate": 0.5593122102009274, "pool_size": 29.0, "champions": "Heimerdinger,Kennen,Hecarim,Quinn,Kassadin,XinZhao,Chogath,Nilah,Trundle,Malzahar,MasterYi,Zilean,TahmKench,Nasus,KogMaw,Pantheon,Yorick,Ivern,Bard,Riven,Taric,Kled,Rammus,Seraphine,Akshan,Fizz,Vladimir,Soraka,Sivir", "crowding_distance": 0.1377161149683615},
    {"win_rate": 0.5583270817704427, "pool_size": 30.0, "champions": "Heimerdinger,Kennen,Annie,Hecarim,Quinn,Kassadin,XinZhao,Chogath,Nilah,Trundle,Malzahar,MasterYi,Zilean,TahmKench,Nasus,KogMaw,Pantheon,Yorick,Ivern,Bard,Riven,Taric,Kled,Rammus,Seraphine,Akshan,Fizz,Vladimir,Soraka,Sivir", "crowding_distance": float('inf')}
]

# Extraindo pool_size e win_rate para o plot
pool_sizes = [data["pool_size"] for data in pareto_data]
win_rates = [data["win_rate"] for data in pareto_data]

# Criando o gráfico de dispersão
plt.figure(figsize=(10, 6))
plt.scatter(pool_sizes, win_rates, color='blue', label='Frente de Pareto', s=50)

# Adicionando rótulos e título
plt.xlabel('Tamanho do Pool (Número de Campeões)', fontsize=12)
plt.ylabel('Taxa de Vitória (Win Rate)', fontsize=12)
plt.title('Frente de Pareto: Trade-off entre Win Rate e Tamanho do Pool', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()

# Ajustando os limites dos eixos para melhor visualização
plt.xlim(0, 32)
plt.ylim(0.55, 0.60)

# Exibindo o gráfico
plt.tight_layout()
plt.savefig("pareto_front_plot.png", dpi=300)  # Salvar como imagem de alta resolução
plt.show()