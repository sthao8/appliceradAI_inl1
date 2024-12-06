import unittest
from filehandler import FileHandler, Package
import os
from decimal import Decimal

class TestFilehandler(unittest.TestCase):
    def setUp(self):
        self.filehandler = FileHandler()
        self.test_package_info = [
            "Paket_id,Vikt,Förtjänst,Deadline",
            "1, 1.0, 2, 1",
            "2, 2.0, 1, 0"
        ]
        self.TEST_FILEPATH = "test_lagerstatus.csv"

        with open(self.TEST_FILEPATH, "w") as f:
            f.writelines("\n".join(self.test_package_info))

    def test_1_creates_packages(self):
        packages_dict = self.filehandler.read_in_lagerstatus(self.TEST_FILEPATH)

        self.assertDictEqual(
            packages_dict,
            {
                1: Package(1, 1.0, Decimal(2),1),
                2: Package(2, 2.0, Decimal(1), 0),
            }
        )

    def tearDown(self):
        if os.path.exists(self.TEST_FILEPATH):
            os.remove(self.TEST_FILEPATH)

if __name__ == "__main__":
    unittest.main()