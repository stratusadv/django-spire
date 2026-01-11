from enum import Enum


class ColumnType(str, Enum):
    TEXT = 'text'
    CHOICE = 'choice'
    NUMBER = 'number'
    DECIMAL_1 = 'decimal_1'
    DECIMAL_2 = 'decimal_2'
    DECIMAL_3 = 'decimal_3'
    DOLLAR = 'dollar'
    PERCENT = 'percent'


