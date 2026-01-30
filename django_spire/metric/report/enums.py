from enum import StrEnum


class ColumnType(StrEnum):
    TEXT = 'text'
    CHOICE = 'choice'
    NUMBER = 'number'
    NUMBER_1 = 'decimal_1'
    NUMBER_2 = 'decimal_2'
    NUMBER_3 = 'decimal_3'
    DOLLAR = 'dollar'
    DOLLAR_1 = 'dollar_1'
    DOLLAR_2 = 'dollar_2'
    DOLLAR_3 = 'dollar_3'
    PERCENT = 'percent'
    PERCENT_1 = 'percent_1'
    PERCENT_2 = 'percent_2'
    PERCENT_3 = 'percent_3'


