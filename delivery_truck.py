from collections import Counter

from package import Package
from constants import Constants

class DeliveryTruck:
    def __init__(self, id: int):
        self.id = id
        self.max_weight = Constants.WEIGHT_LIMIT.value
        self.weight = 0
        self.packages = []

    def total_price(self):
        return sum([package.price for package in self.packages])

    def total_late_fees(self):
        return sum([package.late_fee for package in self.packages])

    def price_category_counts(self):
        return Counter([package.price_category for package in self.packages])

    def deadlines_counts(self):
        return Counter([package.deadline for package in self.packages])

    def load_package(self, package: Package):
        truck_weight = round(self.weight, 2)
        if truck_weight + package.weight > self.max_weight:
            print(f"truck current weight: {self.weight}, package weight: {package.weight}")
            raise ValueError("Loading package weight would exceed maximum weight")

        self.weight = truck_weight + package.weight
        self.packages.append(package)

    def empty_load(self):
        self.weight = 0
        self.packages = []

    def print_report(self):
        print(f"Truck {self.id}: {self.weight} kg, {self.total_price()} profit, {self.total_late_fees()} late fees, \nDistribution of price score: {self.price_category_counts()}\nDistribution of deadlines: {self.deadlines_counts()}\n")