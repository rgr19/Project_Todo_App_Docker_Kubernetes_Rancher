#!/usr/bin/env python3.7

import logging
from pprint import pprint
from types import GeneratorType
from typing import List, ClassVar

logger = logging.getLogger(__name__)

logger.info("Hello logging!")


class Generators(object):
    lst: ClassVar[List[GeneratorType]] = []

    def __init__(self, *gens):
        print(Generators.lst)
        self.adds(*gens)
        print(Generators.lst)

    @staticmethod
    def add(gen):
        print(Generators.lst, gen)
        if isinstance(gen, (list, tuple)):
            Generators.adds(*gen)
        elif isinstance(gen, GeneratorType):
            Generators.lst.append(gen)
        print(Generators.lst)

    @staticmethod
    def adds(*gens):
        print(Generators.lst, gens)
        for g in gens:
            Generators.add(g)
        print(Generators.lst)

    @staticmethod
    def iterate():
        print(Generators.lst)
        for g in Generators.lst:
            yield g

    @staticmethod
    def print():
        for gen in Generators.lst:
            print(gen)
