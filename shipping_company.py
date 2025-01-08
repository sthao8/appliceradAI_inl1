from random import randint
import numpy as np
from numpy import ndarray, dtype, flatiter
from decimal import Decimal

import heapq
from filehandler import FileHandler, Package
from delivery_truck import DeliveryTruck
from constants import Constants

random_generator = np.random.default_rng()

class Solution:
    def __init__(self, packages: list[Package], bitarray: ndarray[bool] = None, weight_limit: float = None, late_fee_weight: float = Constants.LATE_FEE_WEIGHT.value):
        self.packages = packages
        self.amt_packages = len(packages)
        self.weight_limit = weight_limit or Constants.WEIGHT_LIMIT.value
        self.bitarray = bitarray if bitarray is not None else self.generate_random_solutions_limit_by_weight()
        self._late_fee_weight = late_fee_weight
        self.max_profit = max(self.packages, key=lambda package: package.profit).profit
        self.max_late_fee = max(self.packages, key=lambda package: package.late_fee).late_fee

    @property
    def packages_subset(self):
        subset = [self.packages[index] for index in self.bitarray if index]
        return subset

    @property
    def total_profit(self):
        total_profit = 0
        for include_package, package in zip(self.bitarray, self.packages):
            if include_package:
                total_profit += package.profit - package.late_fee
        return total_profit

    @property
    def late_fee_weight(self) -> float:
        return self._late_fee_weight

    def total_weight(self):
        weight = 0
        for package in self.packages_subset:
            weight += package.weight
        return weight

    @late_fee_weight.setter
    def late_fee_weight(self, value: float):
        if not (0 <= value <= 1):
            raise ValueError("late_fee_weight must be between 0 and 1")
        self._late_fee_weight = value

    @property
    def fitness(self) -> Decimal:
        """Return a bitarray's total profit if total weight meets weight constraint, else 0"""
        total_weight = 0
        total_normalized_profit = 0
        for include_package, package in zip(self.bitarray, self.packages):
            if include_package:
                total_weight += package.weight
                total_normalized_profit += self.normalize_total_profit(package)

        return total_normalized_profit if total_weight <= self.weight_limit else 0

    def normalize_total_profit(self, package: Package) -> Decimal:
        normalized_profit = Decimal(float(package.profit) / float(self.max_profit)) * Decimal(1 - self.late_fee_weight)
        if self.max_late_fee > 0:
            normalized_late_fee = Decimal(float(package.late_fee) / float(self.max_late_fee)) * Decimal(self.late_fee_weight)
        else:
            normalized_late_fee = 0
        return normalized_profit + normalized_late_fee

    def generate_random_solutions_limit_by_weight(self):
        ALLOWED_MISSES = 100
        bitarray = np.full(self.amt_packages, False, dtype=bool) # TODO just return a list of indices that are true / packages are included
        total_weight = 0
        seen_indices = set() # TODO just return this?
        miss = 0
        while False in bitarray: # Only run when there are still packages to include
            rand_index = randint(0, self.amt_packages - 1)
            if rand_index not in seen_indices:
                if total_weight + self.packages[rand_index].weight > self.weight_limit:
                    # TODO work on optimizing the remaining weight instead of just break
                    miss += 1
                    if miss >= ALLOWED_MISSES: break
                else:
                    bitarray[rand_index] = True
                    total_weight += self.packages[rand_index].weight
                    seen_indices.add(rand_index)
                    miss = 0
        return bitarray

class ShippingCompany:
    def __init__(self, packages: list[Package] = None):
        self.filehandler = FileHandler()
        self.packages = packages or self.filehandler.create_packages_from_file() # TODO we should also tie the amt_packages to this, so include in shipping company
        self.fleet = [DeliveryTruck(id) for id in range(Constants.AMT_TRUCKS.value)]
        self.initial_total_potential_profit = self.calculate_total_potential_profit_minus_loss()

    def load_fleet(self):
        for truck in self.fleet:
            if self.packages:
                print(f"Truck {truck.id}")
                best_solution = self.genetic_algorithm()
                package_indexes = [index for index, boolean_value in enumerate(best_solution.bitarray) if boolean_value]
                for index in package_indexes[::-1]:
                    package = self.packages.pop(index)
                    truck.load_package(package)
            print(f"Truck weight: {truck.weight}")

    def calculate_total_profit(self):
        return sum([truck.profit for truck in self.fleet])

    def calculate_remaining_late_fees(self):
        total_late_fees = 0
        for package in self.packages:
            if package.late_fee > 0:
                total_late_fees += package.late_fee
        return total_late_fees

    def calculate_total_potential_profit_minus_loss(self):
        return sum([package.total_effective_profit for package in self.packages])

    def genetic_algorithm(self) -> Solution:
        """Using genetic algorithm to optimize package delegation"""
        current_generation = self.generate_random_solutions()
        average_fitness_delta = None
        generation = 0
        while average_fitness_delta is None or average_fitness_delta > Constants.AVG_FITNESS_DELTA_THRESHOLD.value:
            next_generation = self.generate_next_generation(current_generation)
            next_generation_avg = self.calculate_average_fitness(next_generation)
            print(f"Generation {generation} fitness average: {next_generation_avg}")
            current_generation_avg = self.calculate_average_fitness(current_generation)

            average_fitness_delta = abs(next_generation_avg - current_generation_avg)
            current_generation = next_generation
            generation += 1

        best = max(current_generation, key=lambda x: x.fitness)
        print(f"best fitness: {best.fitness}, solution weight: {best.total_weight()}")
        return best

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
        parents = []
        for _ in range(2):
            participants = random_generator.choice(sample_population, size = tournament_size)
            parent = max(participants, key=lambda x: x.fitness)
            parents.append(parent)
        return parents

    def produce_two_crossover_children(self, parents: list[Solution], crossover_rate: float = Constants.CROSSOVER_RATE.value) -> tuple[Solution, Solution]:
        # TODO works only with even number elements???!
        # TODO optimize the crossovers by swapper indices over or under upper / 2
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
        mutation_rate_mask = np.random.random(child.bitarray.shape) <= mutation_rate #TODO make a loop instead of a mask
        return np.invert(child.bitarray, where=mutation_rate_mask)