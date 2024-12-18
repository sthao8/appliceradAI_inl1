from package import Package
from decimal import Decimal
import csv
import random

class FileHandler:
    def __init__(self):
        self.lagerstatus_filepath = "lagerstatus.csv"

    def create_packages_from_file(self, filepath: str = None) -> list[Package]:
        with open(filepath or self.lagerstatus_filepath, "r", encoding='utf-8') as lagerstatus_file:
            reader = csv.DictReader(lagerstatus_file)

            packages_list = []

            for package_info in reader:
                package = Package(
                    int(package_info["Paket_id"]),
                    float(package_info["Vikt"]),
                    Decimal(package_info["Förtjänst"]),
                    int(package_info["Deadline"])
                )

                packages_list.append(package)

            return packages_list

    def update_stock_status(self, packages_list: list[Package], filepath: str = None):
        headers = ["Paket_id", "Vikt", "Förtjänst", "Deadline"]

        with open(filepath or self.lagerstatus_filepath, "w", newline='', encoding='utf-8') as lagerstatus_file:
            writer = csv.DictWriter(lagerstatus_file, fieldnames=headers)
            writer.writeheader()
            for package in packages_list:
                writer.writerow(
                    {
                        "Paket_id": package.id,
                        "Vikt": package.weight,
                        "Förtjänst": package.profit,
                        "Deadline": package.days_to_deadline
                    }
                )
