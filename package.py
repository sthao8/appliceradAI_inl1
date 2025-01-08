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
    def late_fee(self) -> Decimal:
        if self.days_to_deadline > 0:
            return Decimal(0)
        return Decimal(self.days_to_deadline**2)

    @property
    def total_effective_profit(self):
        return self.profit - self.late_fee

    def __eq__(self, other):
        return self.id == other.id

if __name__ == '__main__':
    package = Package(1, 0.1, Decimal(10.0), -10)
    print(package.late_fee)