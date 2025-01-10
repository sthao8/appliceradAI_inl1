from enum import Enum

class Constants(Enum):
    WEIGHT_LIMIT = 800
    AMT_TRUCKS = 10

    POPULATION_SIZE = 100
    GENERATIONS = 10
    MAX_GENERATIONS = 500
    AMT_TOURNAMENT_PARTICIPANTS = 8 # should be even number less than population size
    CROSSOVER_RATE = 0.8
    MUTATION_RATE = 0.001
    MAX_MUTATION_RATE = 0.1
    FITNESS_DELTA_THRESHOLD = 0.1

    # per package
    OVERDUE_WEIGHT = 7
    DEADLINE_WEIGHT = 2
    PRICE_CAT_WEIGHT = 1

    # across solution
    WEIGHT_WEIGHT = 3 # 1 worked well too

    ELITISM_PARTICIPANTS = 5
    LAGERSTATUS_FILEPATH = "lagerstatus.csv"