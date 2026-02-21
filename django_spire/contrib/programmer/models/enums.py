from enum import Enum


class ModelActionEnum(str, Enum):
    FIELDS = 'Adjust model fields'
    METHODS = ''
    CREATE = 'cre'
    REVIEW = 'rev'