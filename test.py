import unittest
from filehandler import FileHandler, Package
import os
from decimal import Decimal
from delivery_truck import DeliveryTruck
from shipping_company import ShippingCompany, bitarray


class TestFilehandler(unittest.TestCase):
    def setUp(self):
        self.filehandler = FileHandler()
        self.test_package_info = [
            "Paket_id,Vikt,Förtjänst,Deadline",
            "1, 1.0, 2, 1",
            "2, 2.0, 1, 0"
        ]
        self.TEST_FILEPATH = "test_lagerstatus.csv"

        with open(self.TEST_FILEPATH, "w", encoding='utf-8') as f:
            f.writelines("\n".join(self.test_package_info))

    def test_1_creates_packages(self):
        packages_list = self.filehandler.create_packages_from_file(self.TEST_FILEPATH)

        self.assertListEqual(
            packages_list,
            [
                Package(1, 1.0, Decimal(2),1),
                Package(2, 2.0, Decimal(1), 0),
            ]
        )

    def test_2_update_packages(self):
        packages_list = [
            Package(3, 1.0, Decimal(2),1),
            Package(4, 2.0, Decimal(1), 0),
            Package(5, 2.0, Decimal(1), 0),
        ]

        self.filehandler.update_stock_status(packages_list, self.TEST_FILEPATH)

    def test_3_update_packages_amount_less_than_file(self):
        packages_list = [
            Package(6, 2.0, Decimal(1), 0)
        ]

        self.filehandler.update_stock_status(packages_list, self.TEST_FILEPATH)
    #
    # def tearDown(self):
    #     if os.path.exists(self.TEST_FILEPATH):
    #         os.remove(self.TEST_FILEPATH)

class TestDeliveryTruck(unittest.TestCase):
    def setUp(self):
        self.truck = DeliveryTruck(1)

    def test_1_load_packages_within_max_weight(self):
        package = Package(1, 1.0, Decimal(2), 0)

        self.truck.load_package(package)

        self.assertListEqual(
            self.truck.packages,
            [Package(1, 1.0, Decimal(2), 0)]
        )

    def test_2_raise_error_if_load_package_would_exceed_max_weight(self):
        package = Package(1, 800.1, Decimal(2), 0)

        with self.assertRaises(ValueError):
            self.truck.load_package(package)

    def test_3_unload_package_exists(self):
        package = Package(1, 1.0, Decimal(2), 0)

        self.truck.packages.append(package)

        self.truck.unload_package(package)

        self.assertListEqual(
            self.truck.packages, []
        )

    def test4_unload_package_does_not_exists(self):
        with self.assertRaises(ValueError):
            self.truck.unload_package(Package(100, 100, Decimal(2), 0))

class TestPackage(unittest.TestCase):
    def test_1_returns_0_if_not_late(self):
        package = Package(1, 1.0, Decimal(2), 0)

        self.assertEqual(package.late_fee, 0)

    def test_2_returns_late_fee_when_late(self):
        package = Package(1, 1.0, Decimal(2), -10)

        self.assertEqual(package.late_fee, Decimal(-100))

class TestShippingCompany(unittest.TestCase):
    def test_1_evaluates_fitness_score_within_weight_limit(self):
        test_bitarray = bitarray("110")
        package1 = Package(1, 1, 10, 10)
        package2 = Package(2, 10, 100, 10)
        package3 = Package(3, 10, 100, 10)
        packages = [package1, package2, package3]

        shipping_company = ShippingCompany(packages)

        fitness = shipping_company.evaluate_fitness(test_bitarray, 20)

        self.assertEqual(fitness, 110)

    def test_2_evaluates_fitness_score_above_weight_limit_returns_0(self):
        test_bitarray = bitarray("111")
        package1 = Package(1, 1, 10, 10)
        package2 = Package(2, 10, 100, 10)
        package3 = Package(3, 10, 100, 10)
        packages = [package1, package2, package3]

        shipping_company = ShippingCompany(packages)

        fittest = shipping_company.evaluate_fitness(test_bitarray, 20)

        self.assertEqual(fittest, 0)

    def test_3_generates_random_population(self):
        shipping_company = ShippingCompany()

        with open("test_random_population", "w") as f:
            for rand_bitarray in shipping_company.generate_random_bitarray(10):
                f.write(str(rand_bitarray) + "\n")

if __name__ == "__main__":
    unittest.main()