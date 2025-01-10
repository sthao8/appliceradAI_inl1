from package import Package
import csv
from constants import Constants

class FileHandler:
    def __init__(self):
        self.lagerstatus_filepath = Constants.LAGERSTATUS_FILEPATH.value

    def create_packages_from_file(self, filepath: str = None) -> list[Package]:
        with open(filepath or self.lagerstatus_filepath, "r", encoding='utf-8') as lagerstatus_file:
            reader = csv.DictReader(lagerstatus_file)

            packages_list = []

            for package_info in reader:
                package = Package(
                    int(package_info["Paket_id"]),
                    float(package_info["Vikt"]),
                    int(package_info["Förtjänst"]),
                    int(package_info["Deadline"])
                )

                packages_list.append(package)

            return packages_list