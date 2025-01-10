import copy
from random import randint, uniform

import numpy as np
from collections import Counter

import heapq
from filehandler import FileHandler, Package
from delivery_truck import DeliveryTruck
from constants import Constants

random_generator = np.random.default_rng()

class Solution:
    def __init__(self, packages: list[Package], max_deadline: int, min_deadline:int, include_indices: list[int] = None, weight_limit: float = Constants.WEIGHT_LIMIT.value):
        self.packages = packages
        self.amt_packages = len(self.packages)
        self.weight_limit = weight_limit

        self.include_indices = include_indices if include_indices is not None else self.generate_random_solutions_limit_by_weight()
        self.indices_dirty = True

        self.max_deadline = max_deadline
        self.min_deadline = min_deadline

        self._total_weight = None
        self._fitness = None
        self._average_profit_category = None

    @property
    def count_deadline(self):
        return Counter([self.packages[index].deadline for index in self.include_indices])

    @property
    def total_weight(self):
        self.recalculate()
        return self._total_weight

    @property
    def average_profit_category(self):
        self.recalculate()
        return self._average_profit_category

    @property
    def average_deadline(self):
        summed_deadline = sum([self.packages[index].deadline for index in self.include_indices])
        return summed_deadline / len(self.include_indices)

    @property
    def fitness(self):
        self.recalculate()
        return self._fitness

    def append_index(self, index: int):
        self.include_indices.append(index)
        self.indices_dirty = True

    def remove_index(self, index: int):
        self.include_indices.remove(index)
        self.indices_dirty = True

    def recalculate(self):
        if not self.indices_dirty:
            return

        self.indices_dirty = False

        weight = 0
        for index in self.include_indices:
            package = self.packages[index]
            weight += package.weight
        self._total_weight = weight

        sum_price_cat = 0
        for index in self.include_indices:
            package = self.packages[index]
            sum_price_cat += package.price_category

        self._average_profit_category = sum_price_cat / len(self.include_indices)

        total_weight = 0
        sum_packages_fitness = 0

        for index in self.include_indices:
            package = self.packages[index]
            total_weight += package.weight
            sum_packages_fitness += package.recalculate_fitness(self.min_deadline, self.max_deadline)

        normalized_total_weight = total_weight / Constants.WEIGHT_LIMIT.value * Constants.WEIGHT_WEIGHT.value

        self._fitness = sum_packages_fitness + normalized_total_weight if total_weight <= Constants.WEIGHT_LIMIT.value else 0

    def generate_random_solutions_limit_by_weight(self) -> list[int]:
        ALLOWED_MISSES = 100
        total_weight = 0
        seen_indices = []
        amt_seen_indices = 0
        miss = 0
        while amt_seen_indices < self.amt_packages: # Only run when there are still packages to include
            rand_index = randint(0, self.amt_packages - 1)
            if rand_index not in seen_indices:
                package = self.packages[rand_index]
                if total_weight + package.weight > self.weight_limit:
                    miss += 1
                    if miss > ALLOWED_MISSES: break
                else:
                    total_weight += package.weight
                    seen_indices.append(rand_index)
                    amt_seen_indices += 1
                    miss = 0
        return seen_indices

class ShippingCompany:
    def __init__(self, packages: list[Package] = None):
        self.filehandler = FileHandler()
        self.packages = packages or self.filehandler.create_packages_from_file()
        self.fleet = [DeliveryTruck(id) for id in range(Constants.AMT_TRUCKS.value)]
        self.initial_late_fees = self.calculate_late_fees(self.packages)

    def calculate_late_fees(self, packages: list[Package]):
        return sum([package.late_fee for package in packages])

    def calculate_late_fees_fleet(self):
        total_late_fees = 0
        for truck in self.fleet:
            total_late_fees += self.calculate_late_fees(truck.packages)
        return total_late_fees

    def calculate_profit_fleet(self):
        total_profit = 0
        for truck in self.fleet:
            total_profit += self.sum_price_category(truck.packages)
        return total_profit

    def calculate_sum_price_inventory(self):
        return self.sum_price_category(self.packages)

    def sum_price_category(self, packages: list[Package]):
        return sum([package.price_category for package in packages])

    @property
    def amt_packages(self) -> int:
        return len(self.packages)

    @property
    def max_deadline(self):
        return max(self.packages, key=lambda package: package.deadline).deadline

    @property
    def min_deadline(self):
        return min(self.packages, key=lambda package: package.deadline).deadline

    def load_fleet(self):
        for truck in self.fleet:
            if self.packages:
                print(f"Truck {truck.id}")
                best_solution = self.genetic_algorithm()
                sorted_reversed_indices = sorted(best_solution.include_indices, reverse=True)
                for index in sorted_reversed_indices:
                    package = self.packages.pop(index)
                    truck.load_package(package)
            print(f"Truck weight: {truck.weight}")

    def genetic_algorithm(self) -> Solution:
        current_generation = self.generate_random_solutions()
        generation = 0
        current_generation_avg = self.calculate_average_fitness(current_generation)
        current_best = max(current_generation, key=lambda x: x.fitness)
        worst = min(current_generation, key=lambda x: x.fitness)
        print(f"Generation {generation} fitness average: {current_generation_avg:.2f}, best: {current_best.fitness:.2f}, worst: {worst.fitness:.2f}")

        counter_avg_seen = 0
        while counter_avg_seen < Constants.GENERATIONS.value and generation < Constants.MAX_GENERATIONS.value:
            generation += 1

            next_generation = self.generate_next_generation(current_generation, counter_avg_seen)
            next_generation_avg = self.calculate_average_fitness(next_generation)
            next_best = max(current_generation, key=lambda x: x.fitness)
            worst = min(current_generation, key=lambda x: x.fitness)
            print(f"Generation {generation} average fitness: {next_generation_avg:.2f}, best: {next_best.fitness:.2f}, worst: {worst.fitness:.2f}")

            if abs(current_best.fitness - next_best.fitness) <= Constants.FITNESS_DELTA_THRESHOLD.value:
                counter_avg_seen += 1
            else:
                counter_avg_seen = 0

            current_generation = next_generation
            current_best = next_best

        best_solution = max(current_generation, key=lambda x: x.fitness)
        print(f"best fitness: {best_solution.fitness:.2f}, weight: {best_solution.total_weight:.2f}, avg price category: {best_solution.average_profit_category:.2f}, avg deadline: {best_solution.average_deadline:.2f}")
        print(f"package deadline distribution: {best_solution.count_deadline}")
        return best_solution

    def generate_next_generation(self, old_generation: list[Solution], counter_avg_seen: int):
        new_population = []
        elite_solutions = heapq.nlargest(Constants.ELITISM_PARTICIPANTS.value, old_generation, key=lambda x: x.fitness)
        new_population += [copy.deepcopy(solution) for solution in elite_solutions]

        while len(new_population) < Constants.POPULATION_SIZE.value:
            two_parents = self.select_tournament_winner_parents(old_generation, Constants.AMT_TOURNAMENT_PARTICIPANTS.value)
            child1, child2 = self.produce_two_children(two_parents)

            new_population.append(self.mutate_solution(child1, counter_avg_seen))
            new_population.append(self.mutate_solution(child2, counter_avg_seen))

        return new_population

    def calculate_average_fitness(self, population: list[Solution]):
        return sum([solution.fitness for solution in population]) / len(population)

    def generate_random_solutions(self, population_size: int = Constants.POPULATION_SIZE.value) -> list[Solution]:
        return [Solution(self.packages, self.max_deadline, self.min_deadline) for _ in range(population_size)]

    def select_tournament_winner_parents(self, population: list[Solution], tournament_size: int):
        parents = []
        for _ in range(2):
            participants = random_generator.choice(population, size = tournament_size)
            parent = max(participants, key=lambda x: x.fitness)
            parents.append(parent)
        return parents

    def produce_two_children(self, parents: list[Solution], crossover_rate: float = Constants.CROSSOVER_RATE.value) -> tuple[Solution, Solution]:
        parent1, parent2 = parents

        if not random_generator.random() <= crossover_rate:
            return parent1, parent2

        parent1_half_1, parent1_half_2 = self.splice_parent(parent1)
        parent2_half_1, parent2_half_2 = self.splice_parent(parent2)

        child1 = Solution(self.packages, self.max_deadline, self.min_deadline, include_indices=parent1_half_1 + parent2_half_2)
        child2 = Solution(self.packages, self.max_deadline, self.min_deadline, include_indices=parent2_half_1 + parent1_half_2)

        return child1, child2

    def splice_parent(self, parent: Solution) -> tuple[list[int], list[int]]:
        half_1 = []
        half_2 = []
        middle_index = self.amt_packages // 2
        for index in parent.include_indices:
            if index < middle_index:
                half_1.append(index)
            else:
                half_2.append(index)
        return half_1, half_2

    def mutate_solution(self, solution: Solution, counter_avg_seen):
        solution_copy = copy.deepcopy(solution)

        mutation_rate = Constants.MUTATION_RATE.value * counter_avg_seen
        if mutation_rate > Constants.MAX_MUTATION_RATE.value: mutation_rate = Constants.MAX_MUTATION_RATE.value

        for index in range(self.amt_packages):
            if uniform(0, 1) <= mutation_rate:
                if index in solution_copy.include_indices:
                    solution_copy.remove_index(index)
                else:
                    solution_copy.append_index(index)
        return solution_copy

    def increment_late_days(self):
        for package in self.packages:
            package.deadline -= 1
            print(package.deadline)
        print("days to deadline decremented")

    def reset_fleet(self):
        for truck in self.fleet:
            truck.empty_load()