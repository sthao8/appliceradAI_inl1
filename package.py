from decimal import Decimal
from datetime import date, timedelta
from typing import Union


class Package():
    def __init__(self, id: int, weight: float, profit: Decimal, days_to_deadline: int):
        self.id = id
        self.weight = weight
        self.profit = profit
        self.days_to_deadline = days_to_deadline

    @property
    def late_fee(self) -> Union[Decimal, int]:
        if not self.days_to_deadline < 0:
            return 0
        return Decimal(-(self.days_to_deadline**2))

    def __eq__(self, other):
        return self.id == other.id and self.weight == other.weight and self.profit == other.profit and self.days_to_deadline == other.days_to_deadline


if __name__ == '__main__':
    package = Package(1, 0.1, Decimal(10.0), -10)
    print(package.late_fee)