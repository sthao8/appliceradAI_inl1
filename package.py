from constants import Constants

class Package():
    def __init__(self, id: int, weight: float, price_category: int, days_to_deadline):
        self.id = id
        self.weight = weight
        self.price_category = price_category
        self._days_to_deadline = days_to_deadline
        self.late_fee = days_to_deadline ** 2 if days_to_deadline < 0 else 0

    @property
    def deadline(self):
        return self._days_to_deadline

    @deadline.setter
    def deadline(self, days_to_deadline):
        self._days_to_deadline = days_to_deadline

    def recalculate_fitness(self, min_deadline: int, max_deadline: int):
        normalized_price_category = (self.price_category / 10) * Constants.PRICE_CAT_WEIGHT.value

        if self.deadline < 0 and min_deadline != 0:  # overdue packages
            normalized_deadline_penalty = self.deadline / min_deadline * Constants.OVERDUE_WEIGHT.value
        elif self.deadline > 0 and max_deadline != 0: # invert to prioritize packages with lower values
            normalized_deadline_penalty = (1 - self.deadline / max_deadline) * Constants.DEADLINE_WEIGHT.value
        else:
            normalized_deadline_penalty = 0

        return normalized_price_category + normalized_deadline_penalty
