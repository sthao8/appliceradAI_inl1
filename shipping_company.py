from typing import Generator, Union, List, Tuple
import random
import numpy as np
from numpy import ndarray, dtype

import heapq
from filehandler import FileHandler, Package
from delivery_truck import DeliveryTruck
from constants import Constants

random_generator = np.random.default_rng()

class Solution:
    def __init__(self, packages: list[Package], bitarray: ndarray[bool] = None, amt_packages: int = Constants.AMT_PACKAGES.value, weight_limit: float = None):
        self.bitarray = bitarray if bitarray is not None else random_generator.choice([True, False], size = amt_packages)
        self.weight_limit = weight_limit or Constants.WEIGHT_LIMIT.value
        self.fitness = self.evaluate_fitness(packages)

    def evaluate_fitness(self, packages: list[Package]) -> float:
        """Return a bitarray's total profit if total weight meets weight constraint, else 0"""
        total_weight = 0
        total_profit = 0
        for include_package, package in zip(self.bitarray, packages):
            if include_package:
                total_weight += package.weight
                total_profit += package.profit

        return total_profit if total_weight <= self.weight_limit else 0

class ShippingCompany:
    def __init__(self, packages: list[Package] = None):
        self.filehandler = FileHandler()
        self.packages = packages or self.filehandler.create_packages_from_file() # TODO we should also tie the amt_packages to this, so include in shipping company
        self.fleet = [DeliveryTruck(id) for id in range(Constants.AMT_TRUCKS.value)]

    def genetic_algorithm(self) -> Solution:
        """Using genetic algorithm to optimize package delegation"""
        current_generation = self.generate_random_solutions()
        current_generation_avg = self.calculate_average_fitness(current_generation)

        average_fitness_delta = None
        while not average_fitness_delta or average_fitness_delta < Constants.AVG_FITNESS_DELTA_THRESHOLD.value:
            next_generation = self.generate_next_generation(current_generation)
            next_generation_avg = self.calculate_average_fitness(next_generation)
            average_fitness_delta = abs(next_generation_avg - current_generation_avg)
            current_generation = next_generation

        return max(current_generation, key=lambda x: x.fitness)

    def generate_next_generation(self, old_generation: list[Solution], population_size: int = Constants.POPULATION_SIZE.value):
        new_population = []
        elite_solutions = heapq.nlargest(2, old_generation, key=lambda x: x.fitness)
        new_population += elite_solutions

        while len(new_population) != population_size:
            two_parents = self.select_tournament_winner_parents(old_generation, Constants.AMT_TOURNAMENT_PARTICIPANTS.value)
            child1, child2 = self.produce_two_crossover_children(two_parents)

            new_population.append(child1)
            new_population.append(child2)

        return new_population

    def calculate_average_fitness(self, generation: list[Solution]):
        fitness_sum = sum([solution.fitness for solution in generation])
        return fitness_sum / len(generation)

    def generate_random_solutions(self, population_size: int = Constants.POPULATION_SIZE.value) -> list[Solution]:
        return [Solution(self.packages) for _ in range(population_size)]

    def select_tournament_winner_parents(self, sample_population: list[Solution], tournament_size: int):
        parents = ()
        for _ in range(2):
            participants = random_generator.choice(sample_population, size = tournament_size)
            parent = max(participants, key=lambda x: x.fitness)
            parents += (parent, )
        return parents

    def produce_two_crossover_children(self, parents: list[Solution], crossover_rate: float = Constants.CROSSOVER_RATE.value) -> tuple[Solution, Solution]:
        # TODO works only with even number elements???!
        parent1, parent2 = parents

        if not random_generator.random() <= crossover_rate:
            return parent1, parent2

        middle_index =  parent1.bitarray.size // 2

        parent1_slice_1, parent1_slice_2 = parent1.bitarray[:middle_index], parent1.bitarray[middle_index:]
        parent2_slice_1, parent2_slice_2 = parent2.bitarray[:middle_index], parent2.bitarray[middle_index:]

        child1 = Solution(self.packages, np.concatenate((parent1_slice_1, parent2_slice_2)))
        child2 = Solution(self.packages, np.concatenate((parent2_slice_1, parent1_slice_2)))

        return child1, child2

    def mutate_child(self, child: Solution, mutation_rate: float = Constants.MUTATION_RATE.value):
        mutation_rate_mask = np.random.random(child.bitarray.shape) <= mutation_rate
        return np.invert(child.bitarray, where=mutation_rate_mask)