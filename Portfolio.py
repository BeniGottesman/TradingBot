"""Portfolio.py"""

# https://refactoring.guru/fr/design-patterns/composite/python/example

import string
from typing import List
from matplotlib import pyplot as plt
import numpy as np
from pandas import DataFrame
import BinanceClient
from datetime import date
from __future__ import annotations


class AbstractPortfolio:
    """
    The base Component class declares common operations for both simple and
    complex objects of a composition.
    """

    @property
    def parent(self) -> AbstractPortfolio:
        return self._parent

    @parent.setter
    def parent(self, parent: AbstractPortfolio):
        """
        Optionally, the base Component can declare an interface for setting and
        accessing a parent of the component in a tree structure. It can also
        provide some default implementation for these methods.
        """

        self._parent = parent

    """
    In some cases, it would be beneficial to define the child-management
    operations right in the base Component class. This way, you won't need to
    expose any concrete component classes to the client code, even during the
    object tree assembly. The downside is that these methods will be empty for
    the leaf-level components.
    """

    def add(self, component: AbstractPortfolio) -> None:
        pass

    def remove(self, component: AbstractPortfolio) -> None:
        pass

    def is_composite(self) -> bool:
        """
        You can provide a method that lets the client code figure out whether a
        component can bear children.
        """

        return False

    @abstractmethod
    def operation(self) -> str:
        """
        The base Component may implement some default behavior or leave it to
        concrete classes (by declaring the method containing the behavior as
        "abstract").
        """

        pass
    
    def value(self) -> str:
        """
        The base Component may implement some default behavior or leave it to
        concrete classes (by declaring the method containing the behavior as
        "abstract").
        """

        pass

# Leaf
class Pair(AbstractPortfolio):
    def __init__(self, pairString) -> None:
        self.pairString = pairString
        self.numberOfShares = 0
        self.BaseCurrentValue = 0
        self.QuoteCurrentValue = 0

    def getPair(self)-> str:
        return "Pair = "+self.pairString

    def operation(self) -> str:
        return "Pair = "

    def value(self) -> str:
        return self.QuoteCurrentValue

# Composite
class Portfolio(AbstractPortfolio):
    """
    The Composite class represents the complex components that may have
    children. Usually, the Composite objects delegate the actual work to their
    children and then "sum-up" the result.
    """

    def __init__(self, quoteCurrency: string) -> None:
        self._children: List[AbstractPortfolio] = []
        self._quoteCurrency = quoteCurrency

    def add(self, abspf: AbstractPortfolio) -> None:
        self._children.append(abspf)
        abspf.parent = self

    def remove(self, abspf: AbstractPortfolio) -> None:
        self._children.remove(abspf)
        abspf.parent = None

    def is_composite(self) -> bool:
        return True

    def getPortfolioCurrency (self) -> string:
        return self._quoteCurrency

    def value(self) -> str:
        TCV = 0
        for child in self._children:
            TCV += child.value()
        return TCV

    def operation(self) -> str:
        """
        The Composite executes its primary logic in a particular way. It
        traverses recursively through all its children, collecting and summing
        their results. Since the composite's children pass these calls to their
        children and so forth, the whole object tree is traversed as a result.
        """

        results = []
        for child in self._children:
            results.append(child.operation())
        return f"Branch({'+'.join(results)})"


if __name__ == "__main__":
    tree = Portfolio()

    branch1 = Portfolio()
    branch1.add(Pair())
    branch1.add(Pair())

    branch2 = Portfolio()
    branch2.add(Pair())

    tree.add(branch1)
    tree.add(branch2)