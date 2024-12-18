from enum import Enum

class Constants(Enum):
    WEIGHT_LIMIT = 20
    AMT_TRUCKS = 10
    POPULATION_SIZE = 10
    AMT_PACKAGES = 7
    AMT_TOURNAMENT_PARTICIPANTS = 4 # should be even number
    MUTATION_RATE = 0.08
    CROSSOVER_RATE = 0.8
    AVG_FITNESS_DELTA_THRESHOLD = 0.1