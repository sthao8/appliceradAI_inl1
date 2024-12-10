from bitarray import util, bitarray
from typing import Generator, Union, List, Tuple
import random
import numpy as np

from filehandler import FileHandler, Package
from delivery_truck import DeliveryTruck
from constants import Constants

class Solution:
    def __init__(self, amt_packages: int = Constants.AMT_PACKAGES.value):
        self.bitarray = util.urandom(amt_packages)
        self.fitness = self.evaluate_fitness(self.bitarray)

    def evaluate_fitness(self, candidate_bitarray: bitarray, packages: list[Package], weight_limit: float = Constants.WEIGHT_LIMIT.value) -> float:
        """Return a bitarray's total profit if total weight meets weight constraint, else 0"""
        total_weight = 0
        total_profit = 0
        for binary_value, package in zip(candidate_bitarray, packages):
            if binary_value == 1:
                total_weight += package.weight
                total_profit += package.profit

        return total_profit if total_weight <= weight_limit else 0

class ShippingCompany:
    def __init__(self, packages: list[Package] = None):
        self.filehandler = FileHandler()
        self.packages = packages or self.filehandler.create_packages_from_file()
        self.fleet = [DeliveryTruck(id) for id in range(Constants.AMT_TRUCKS.value)]

    def delegate_packages(self):
        """Using genetic algorithm to optimize package delegation"""
        pass

    def genetic_selection(self):
        random_population = self.generate_random_solutions()

        elite_solution = max(random_population, key=lambda x: x.fitness)
        next_generation = [random_population.pop(elite_solution)]

        tournament_winner =

    def generate_random_solutions(self, amt_solutions: int = Constants.POPULATION_SIZE.value) -> list[Solution]:
        return [Solution() for _ in range(amt_solutions)]

    def pop_random_element(self, target_list: list):
        list_length = len(target_list)
        return target_list.pop(random.randint(0, list_length-1))

    def find_tournament_winner(self, random_population: list[Solution], tournament_size: int):
        round_participants = [random_population.choice]

