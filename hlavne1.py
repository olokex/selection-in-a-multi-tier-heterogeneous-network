from sys import stderr
import matplotlib.pyplot as plt
import random
import math
import operator

MACROCELL_RESOURCE_BLOCKS = 100
SMALLCELL_RESOURCE_BLOCKS = 50



SMALLCELL_PRICE = 0
MACROCELL_PRICE = 0
SMALLCELL_SIGMA_GAUSS = 0
MACROCELL_SIGMA_GAUSS = 0

MACROCELL_PROBABILITY = 50
SMALLCELL_PROBABILITY = 50




MIN_POSITION = 0
MAX_POSITION = 1000


BOUNDARY = 50

MOBILE_STATION_HEIGHT = 1.7
USER_MIN_THROUGHPUT = 300_000
NOISE_TARAS = 1.8 * math.pow(10, -12)
MAX_CONNECTIONS = 10

CELLS = []
CONNECTED = {}
STATISTICS = {}


RADIUS = 100


RUNS = 300


class Position:

    def generate_position(self, min, max, boundary):
        self.x = random.randint(min + boundary, max - boundary)
        self.y = random.randint(min + boundary, max - boundary)
    

    def get_position(self):
        return self.x, self.y



class Macrocell(Position):
    transmit_power_Pi = 40.5 # W
    height_hb = 25 # m
    carrier_frequency_f = 2100 # MHz


    def __init__(self):
        self.price = random.gauss(MACROCELL_PRICE, MACROCELL_SIGMA_GAUSS)
        self.resource_blocks_used = 0
        self.throughput = math.inf
        self.resource_blocks = MACROCELL_RESOURCE_BLOCKS
    

    def get_throughput(self):
        return self.throughput  
        


class Smallcell(Position):
    transmit_power_Pi = 6.3 # W
    height_hb = 3.5 # m
    carrier_frequency_f = 2100 #MHz


    def __init__(self):
        self.price = random.gauss(SMALLCELL_PRICE, SMALLCELL_SIGMA_GAUSS)
        self.resource_blocks_used = 0
        self.throughput = math.inf
        self.resource_blocks = SMALLCELL_RESOURCE_BLOCKS
      

    def get_throughput(self):
        return self.throughput



class Cells:
    def __init__(self, amount, type_of_cell):
        self.cells = []
        self._find_non_coliding(amount, type_of_cell)


    def get_xs(self):
        return list(map(operator.attrgetter("x"), self.cells))
    

    def get_ys(self):
        return list(map(operator.attrgetter("y"), self.cells))
    

    def __getitem__(self, index):
        return self.cells[index]
    

    def __add__(self, other):
        return self.cells + other.cells


    def _find_non_coliding(self, amount, type_of_cell):
        attempts = 0
        while len(self.cells) < amount and attempts < 100:
            new_cell = type_of_cell()
            new_cell.generate_position(MIN_POSITION, MAX_POSITION, BOUNDARY)
            attempts += 1
            if all(measure_distance(cell, new_cell) > RADIUS for cell in CELLS):
                self.cells.append(new_cell)
                CELLS.append(new_cell)
                attempts = 0
     


class User(Position):
    

    def __init__(self, preference, min_throughput, max_price, resource_wanted, type_of_contract):
        self.preference = preference
        self.min_throughput = min_throughput
        self.max_accepted_price = max_price
        self.resource_wanted = resource_wanted
        self.type_of_contract = type_of_contract
        self.connected_to_cell = None
    

    def utility_function(self, throughput, price_for_service):
        return self.preference * (throughput - self.min_throughput) + (1 - self.preference) * (self.max_accepted_price - price_for_service)
    

    def connect(self, cell):
        self.connected_to_cell = cell
        self.connected_to_cell.resource_blocks_used += self.resource_wanted
    

    def disconnect(self):
        self.connected_to_cell.resource_blocks_used -= self.resource_wanted
        self.connected_to_cell = None



def generate_users(number_of_users, gamma):
    users = []
    
    for _ in range(number_of_users):

        # preference = random.random()
        

        min_throughput = random.randint(0, 1000)
        

        max_price = random.gauss(150, 250)
        

        resource_blocks_wanted = random.randint(1, 5)
        

        type_of_contract = random.choices([Smallcell, Macrocell], weights=(SMALLCELL_PROBABILITY, MACROCELL_PROBABILITY))[0]
        
        u = User(gamma, min_throughput, max_price, resource_blocks_wanted, type_of_contract)
        # u = User(preference, min_throughput, max_price, resource_blocks_wanted)
        u.generate_position(MIN_POSITION, MAX_POSITION, BOUNDARY)
        users.append(u)
        
    return users



class Pair:
    def __init__(self, cell, preference, distance):
        self.cell = cell
        self.preference = preference
        self.distance = distance


    def __repr__(self):
        return f"preference: {self.preference}, distance: {self.distance}"



def connect_two_points(point1, point2):
    # p1x, p1y = point1.x, point1.y
    # p2x, p2y = point2.x, point2.y
    # line = plt.plot([p1x, p2x], [p1y, p2y], 'r-', linewidth=0.5)
    # CONNECTED[point1] = {"cell": point2, "line": line}
    CONNECTED[point1] = True
        


def measure_distance(point1, point2):
    p1x, p1y = point1.x, point1.y
    p2x, p2y = point2.x, point2.y

    return math.sqrt((p1x - p2x)**2 + (p1y - p2y)**2)



def calculate_for_cell_selection(users, cells):
    users_options = {}
    
    for user in users:
        users_options[user] = []
        for cell in cells:
            utility = user.utility_function(cell.get_throughput(), cell.price)
            distance = measure_distance(user, cell)
            users_options[user].append(Pair(cell, utility, distance))
            
    return users_options



def sort_users_option(users):
    for user, _ in users.items():

        # users[user] = sorted(users[user], key=lambda elem: (elem.preference, elem.distance))

        users[user] = sorted(users[user], key=lambda elem: (elem.distance, elem.preference))



def get_total_interference(current_cell, end_user, interference_cells, log10_f, log10_hb, correction, Tx_dBm):
    total_int_mW = 0.0
    
    for cell in interference_cells:
        if cell != current_cell:
            distance = measure_distance(end_user, cell)
            
            if distance < 0.0009:
                distance = 0.001
            path_loss_interference = 69.55 + 26.16 * log10_f - 13.82 * log10_hb - correction + (
                    44.9 - 6.55 * log10_hb) * math.log10(distance)
            interference_dB = Tx_dBm - path_loss_interference
            interference_mW = math.pow(10, (interference_dB / 10))
            total_int_mW += interference_mW
    
    return total_int_mW



def calculate_SNR(end_user, current_cell, intereference_cells):
    distance = measure_distance(end_user, current_cell)
    if distance <= 0.1:
        distance = 0.1

    log10_f = math.log10(current_cell.carrier_frequency_f)
    log10_hb = math.log10(current_cell.height_hb)
    Tx_dBm = 10 * math.log10(current_cell.transmit_power_Pi) + 30

    correction = (1.1 * log10_f - 0.7) * MOBILE_STATION_HEIGHT - (1.56 * log10_f - 0.8)

    path_loss_hata = 46.3 + 33.9 * log10_f - 13.82 * log10_hb - correction + (44.9 - 6.55 * log10_hb) * math.log10(
        distance)
    P_received_dB = Tx_dBm - path_loss_hata
    P_received_mW = math.pow(10, (P_received_dB / 10))
    tot_int = get_total_interference(current_cell, end_user, intereference_cells, log10_f, log10_hb, correction, Tx_dBm)
    sinr = P_received_mW / (tot_int + NOISE_TARAS)
    sinr_dB = 10 * math.log10(sinr)

    throughput = 180000 * math.log2(1 + sinr) * end_user.resource_wanted
    # current_cell.SINR = sinr_dB
    
    # return sinr_dB
    return throughput



def find_suitable_connections(users):

    for user in users:
        for cell in CELLS:
            cell.throughput = calculate_SNR(user, cell, CELLS)
    
    users_option = calculate_for_cell_selection(users, CELLS)

    sort_users_option(users_option)


    for user in users_option:
        for i in range(len(CELLS)):
            option = users_option[user][i]
            if option.cell.resource_blocks_used + user.resource_wanted <= option.cell.resource_blocks:
                connect_two_points(user, option.cell)
                user.connect(option.cell)
                STATISTICS[user]["throughput"].append(option.cell.throughput)        
                STATISTICS[user]["price"].append(option.cell.price)        
                break
        else:
            break
            # print("All stations are fully occupied.", file=stderr)



def find_contracted_connections(users):

    for user in users:
        for cell in CELLS:
            cell.throughput = calculate_SNR(user, cell, CELLS)
    

    random.shuffle(users)
    
    for user in users:
        for _ in range(100):

            cell = random.choice(CELLS)
            if cell.resource_blocks_used + user.resource_wanted <= cell.resource_blocks and isinstance(cell, user.type_of_contract):
                connect_two_points(user, cell)
                user.connect(cell)
                STATISTICS[user]["throughput"].append(cell.throughput)        
                STATISTICS[user]["price"].append(cell.price)
                break


def render(users, macrocells, smallcells):

    user_xs, user_ys = [user.x for user in users], [user.y for user in users]


    plt.scatter(user_xs, user_ys, marker="o", color="green", label="End user")
    plt.scatter(macrocells.get_xs(), macrocells.get_ys(), marker="o", color="orange", label="Macrocell")
    plt.scatter(smallcells.get_xs(), smallcells.get_ys(), marker="o", color="blue", label="Smallcell")
    

def main(parameters, search_function):

    macrocells = Cells(parameters["no_macrocells"], Macrocell)
    smallcells = Cells(parameters["no_smallcells"], Smallcell)
    

    # macrocells[0].x = 10
    # macrocells[0].y = 10
    

    users = generate_users(parameters["no_users"], parameters["gamma"])
    

    for user in users:
        STATISTICS[user] = {
            "throughput": [],
            "price": [],
        }
    
    not_connected_average = 0
    overall_throughput = 0
    price_average = []
    

    for i in range(parameters["steps"]):
        search_function(users)
        
        not_connected_average += parameters["no_users"] - len(CONNECTED)
        

        for user in users:
            if user not in CONNECTED:
                continue
            
            user.disconnect()
            # connection = CONNECTED[user]["line"].pop()
            # connection.remove()
            CONNECTED.pop(user)
            user.generate_position(MIN_POSITION, MAX_POSITION, BOUNDARY)

    search_function(users)


    decimals = 0.6

    for user in users:
        throughputs = STATISTICS[user]["throughput"]
        prices = STATISTICS[user]["price"]
        

        if len(throughputs) <= 0:
            continue
        
        stat = sum(throughputs)/len(throughputs)
        overall_throughput += stat
        avg_price = sum(prices)/len(prices)
        price_average.append(avg_price)
        # print(f"{user}: average throughput: {stat:{decimals}f}")
        # print(f"{user}: average price: {avg_price:{decimals}f}")
        
    # print(f"for all users throughput: {overall_throughput/len(users):{decimals}f}")
    # print("Not connected users", connected_average / parameters["steps"])
    
    # plt.title("Heteregeneous network")
    # render(users, macrocells, smallcells)
    # plt.legend()
    # plt.show()
    
    output_for_simulation = {
        "throughput": overall_throughput/len(users),
        "price": sum(price_average)/len(price_average),
        "not_connected": not_connected_average/parameters["steps"]
    }
    
    return output_for_simulation
  

if __name__ == "__main__":
    pass
