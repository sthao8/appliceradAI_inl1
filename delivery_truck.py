from typing import Union


from package import Package
from constants import Constants

class DeliveryTruck:
    def __init__(self, id: int):
        self.id = id
        self.max_weight = Constants.WEIGHT_LIMIT.value
        self.weight = 0
        self.packages = []

    @property
    def profit(self):
        return sum([package.profit - package.late_fee for package in self.packages])

    def load_package(self, package: Package):
        if self.weight + package.weight > self.max_weight:
            print(f"truck current weight: {self.weight}, package weight: {package.weight}")
            raise ValueError("Loading package weight would exceed maximum weight")

        self.weight += package.weight
        self.packages.append(package)

    def unload_package(self, package: Package) -> None:
        if not package in self.packages:
            raise ValueError(f"Package {package} not found in truck")
        self.packages.remove(package)

    def print_report(self):
        print(f"Truck {self.id}: {self.weight} kg, {self.profit} sek")