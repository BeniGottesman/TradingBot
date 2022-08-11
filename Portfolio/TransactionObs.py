# https://refactoring.guru/fr/design-patterns/observer/python/example
import Portfolio
from typing import List

class TransactionsViewer(Observer):
    def __init__(self) -> None:
        __transaction__ : List[dict] = []

    def update(self, subject: AbstractPortfolio) -> None:
        __transaction__ = subject.report()