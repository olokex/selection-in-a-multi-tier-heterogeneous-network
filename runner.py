import importlib
import stat

model = __import__('hlavne1')

parameters = {
    "no_macrocells": 2,
    "no_smallcells": 10,
    "no_users": 550,
    "steps": 10,
    "gamma": 0.5,
    "runs": 50
}

stats = {
    "throughput": 0,
    "price": 0,
    "not_connected": 0,
}
avg_stat = 0
for _ in range(parameters["runs"]):
    importlib.reload(model)
    model.SMALLCELL_PRICE = 0.5
    model.MACROCELL_PRICE = 0.8
    model.SMALLCELL_SIGMA_GAUSS = 0.5
    model.MACROCELL_SIGMA_GAUSS = 0.5
    model.MACROCELL_PROBABILITY = 50
    model.SMALLCELL_PROBABILITY = 50

    
    #stat = model.main(parameters, model.find_suitable_connections)
    stat = model.main(parameters, model.find_contracted_connections)
    
    for key, value in stat.items():
        stats[key] += value


for key, value in stats.items():
    print(f'average {key} for all runs: {value/parameters["runs"]:5f}')

print(f'price per throughput {stats["throughput"] / stats["price"]:5f}')
    
    