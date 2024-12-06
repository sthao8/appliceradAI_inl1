from package import Package
from decimal import Decimal
import csv

class FileHandler:
    def __init__(self):
        self.lagerstatus_filepath = "lagerstatus.csv"

    def read_in_lagerstatus(self, filepath: str = None):
        with open(filepath or self.lagerstatus_filepath, "r") as lagerstatus_file:
            reader = csv.DictReader(lagerstatus_file)

            packages_dict = {}

            for package_info in reader:
                package = Package(
                    int(package_info["Paket_id"]),
                    float(package_info["Vikt"]),
                    Decimal(package_info["Förtjänst"]),
                    int(package_info["Deadline"])
                )

                packages_dict[package.id] = package

            return packages_dict