import simpy
import random
import statistics
# Goal: find the optimal number of securty personel that gives an average wait time of <20 min.
# Airport process steps:
# 1. Arrive at airport
# 2. Choose to park car if self driven
# 3. Buy/download ticket at pc station
# 4. Wait in line to get bag checked
# 5. Wait in line at security gate
# 6. Go find terminal

wait_times = []

class Airport:
    def __init__(self, env, num_spots, num_stations, num_checkers, num_tsa):
        self.env = env
        self.park = simpy.Resource(env, num_spots)
        self.station = simpy.Resource(env, num_stations)
        self.checker = simpy.Resource(env, num_checkers)
        self.security = simpy.Resource(env, num_tsa)
    def park_car(self, traveler):
        yield self.env.timeout(random.randint(1.0, 3.0))
    def get_ticket(self, traveler):
        yield self.env.timeout(random.triangular(low=1.0, high=6.0, mode=2.5))
    def check_bag(self, traveler):
        yield self.env.timeout(random.randint(2.0, 3.0))
    def security_gate(self, traveler):
        yield self.env.timeout(random.triangular(1.5, 5.0, 2.0))

def go_to_airport(env, traveler, airport):
    # Traveler arrives at the airport
    arrival_time = env.now
    if random.choice([True, False]):
        with airport.park.request() as request:
            yield request
            yield env.process(airport.park_car(traveler))
    with airport.station.request() as request:
        yield request
        yield env.process(airport.get_ticket(traveler))
    with airport.checker.request() as request:
        yield request
        yield env.process(airport.check_bag(traveler))
    with airport.security.request() as request:
        yield request
        yield env.process(airport.security_gate(traveler))
    # Travler heads into terminals
    wait_times.append(env.now - arrival_time)

# Create an instance of an airport and generate travelers
def run_airport(env, num_spots, num_stations, num_checkers, num_tsa):
    airport = Airport(env, num_spots, num_stations, num_checkers, num_tsa)
    for traveler in range(10):
        env.process(go_to_airport(env, traveler, airport))
    while True:
        yield env.timeout(0.5) # Travlers arive at the airport every 30sec
        traveler += 1
        env.process(go_to_airport(env, traveler, airport))

# Function that calculates the avg time a traveler spends
def get_average_wait_time(wait_times):
    average_wait = statistics.mean(wait_times)
def calculate_wait_time(arrival_times, departure_times):
    average_wait = statistics.mean(wait_times)
    minutes, frac_minutes = divmod(average_wait, 1)
    seconds = frac_minutes * 60
    return round(minutes), round(seconds)

# Helper function to get user inputs
def get_user_input():
    num_spots = input("Input # of parking spots: ")
    num_stations = input("Input # of PC ticket stations: ")
    num_checkers = input("Input # of bag checkers: ")
    num_tsa = input("Input # of tsa agents at security gate: ")
    params = [num_spots, num_stations, num_checkers, num_tsa]
    if all(str(i).isdigit() for i in params): # Check input is valid
        params = [int(x) for x in params]
    else:
        print("Invalid input. Simulation will use default values:",
              "\n 500 park spots, 8 stations, 6 checkers, 6 tsa agents.", )
        params = [500, 8, 6, 6]
    return params

def main():
    # random.seed(123)
    num_spots, num_stations, num_checkers, num_tsa = get_user_input()

    env = simpy.Environment()
    env.process(run_airport(env, num_spots, num_stations, num_checkers, num_tsa))
    env.run(until=30) # run simulation for half hour

    mins, secs = get_average_wait_time(wait_times)
    print(
        "Running simulation...",
        f"\nThe average wait time is { mins } minutes and { secs } seconds.",
    )

if __name__ == '__main__':
    main()


