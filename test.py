import unittest
from unittest.mock import MagicMock

from numpy import ndarray
import numpy as np
from unicodedata import decimal

from filehandler import FileHandler, Package
import os
from decimal import Decimal
from delivery_truck import DeliveryTruck
from shipping_company import ShippingCompany, Solution


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
    def test_1_late_fee_returns_0_if_not_late(self):
        package = Package(1, 1.0, Decimal(2), 0)

        self.assertEqual(package.late_fee, Decimal(0))

    def test_2_returns_late_fee_when_late(self):
        package = Package(1, 1.0, Decimal(2), -10)

        self.assertEqual(package.late_fee, Decimal(100))

class TestSolution(unittest.TestCase):
    def test_1_normalizes_package_profit(self):
        test_bitarray = np.fromiter([True, True, True], bool)
        package1 = Package(1, 1, Decimal(2), 1)
        package2 = Package(2, 1, Decimal(2), 1)
        package3 = Package(3, 1, Decimal(2), -1)
        packages = [package1, package2, package3]

        test_solution = Solution(packages, test_bitarray, 10)

        package1_norm_profit = Decimal(2 / 2 * (1-0.5)) + Decimal(0)
        package3_norm_profit = Decimal(2 / 2 * (1 - 0.5)) + Decimal(1 * 0.5)

        self.assertEqual(test_solution.normalize_total_profit(package1), package1_norm_profit)
        self.assertEqual(test_solution.normalize_total_profit(package3), package3_norm_profit)

    def test_2_evaluates_fitness_score_within_weight_limit(self):
        test_bitarray = np.fromiter([True, True, True], bool)
        package1 = Package(1, 1, Decimal(2), 1)
        package2 = Package(2, 1, Decimal(2), 1)
        package3 = Package(3, 100, Decimal(2), 1)
        packages = [package1, package2, package3]

        test_solution = Solution(packages, test_bitarray, 102)

        fitness = test_solution.fitness

        self.assertEqual(fitness, Decimal(1.5))

    def test_3_evaluates_fitness_score_above_weight_limit_returns_0(self):
        test_bitarray = np.fromiter([True, True, True], bool)
        package1 = Package(1, 1, Decimal(2), 1)
        package2 = Package(2, 1, Decimal(2), 1)
        package3 = Package(3, 100, Decimal(2), 1)
        packages = [package1, package2, package3]

        test_solution = Solution(packages, test_bitarray, 10)

        fittest = test_solution.fitness

        self.assertEqual(fittest, 0)

    def test_4_calculates_total_profit(self):
        test_bitarray = np.fromiter([True, True, True], bool)
        package1 = Package(1, 1, Decimal(2), 1)
        package2 = Package(2, 1, Decimal(2), 1)
        package3 = Package(3, 100, Decimal(2), 1)
        packages = [package1, package2, package3]

        test_solution = Solution(packages, test_bitarray, 10)

        self.assertEqual(test_solution.total_profit, Decimal(6))

class TestShippingCompany(unittest.TestCase):
    def test_1_creates_random_solutions(self):
        shipping_company = ShippingCompany([])

        with open("test_random_population", "w") as f:
            for rand_solution in shipping_company.generate_random_solutions(10):
                f.write(str(rand_solution.bitarray) + "\n")

    def test_2_produces_two_crossover_children(self):
        package1 = Package(1, 1, Decimal(2), 1)
        package2 = Package(2, 1, Decimal(2), 1)
        packages = [package1, package2]

        parent1 = Solution(packages, np.fromiter([True, True], bool), 2, 100)
        parent2 = Solution(packages, np.fromiter([False, False], bool), 2, 100)

        shipping_company = ShippingCompany(packages)

        children = shipping_company.produce_two_crossover_children([parent1, parent2], crossover_rate=100)

        self.assertTrue(
            np.array_equal(
                children[0].bitarray,
                np.fromiter([True, False], bool)
            )
        )

        self.assertTrue(
            np.array_equal(
                children[1].bitarray,
                np.fromiter([False, True], bool)
            )
        )

    def test_3_mutates_child(self):
        package1 = Package(1, 1, Decimal(2), 1)
        package2 = Package(2, 1, Decimal(2), 1)
        packages = [package1, package2]

        parent1 = Solution(packages, np.fromiter([True, True], bool), 2, 100)

        shipping_company = ShippingCompany(packages)

        mutated_child = shipping_company.mutate_child(parent1, 100)

        self.assertTrue(
            np.array_equal(
                mutated_child,
                np.fromiter([False, False], bool)
            )
        )

    def test_4_calculates_average_fitness(self):
        mock_solution1 = MagicMock(spec=Solution, fitness = 10)
        mock_solution2 = MagicMock(spec=Solution, fitness = 10)
        mock_solution3 = MagicMock(spec=Solution, fitness = 10)
        generation = [mock_solution2, mock_solution1, mock_solution3]

        shipping_company = ShippingCompany()

        average = shipping_company.calculate_average_fitness(generation)

        self.assertEqual(average, 10)

if __name__ == "__main__":
    unittest.main()