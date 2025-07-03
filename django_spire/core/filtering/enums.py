from enum import Enum


class QuerySetFilterCommandEnum(Enum):
    SEARCH = 'search'
    FILTER = 'filter'
    CLEAR = 'clear'