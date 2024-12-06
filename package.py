from decimal import Decimal
from datetime import date, timedelta

class Package():
    def __init__(self, id: int, weight: float, profit: Decimal, days_to_deadline: int):
        self.id = id
        self.weight = weight
        self.profit = profit
        self.days_to_deadline = timedelta(days=days_to_deadline)

    def __eq__(self, other):
        return self.id == other.id and self.weight == other.weight and self.profit == other.profit and self.days_to_deadline == other.days_to_deadline

