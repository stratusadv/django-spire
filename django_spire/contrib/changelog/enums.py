from enum import Enum


class ChangeLogTypeEnum(Enum):
    BUG_FIX = ('bug', 'Bug Fix')
    CHANGE = ('chan', 'Change')
    FEATURE = ('feat', 'Feature')
