from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class Budget:
    """
    Бюджет.
    срок,
    категория расходов,
    сумма.

    """
    term: datetime
    amount: int
    category: int
    pk: int = 0