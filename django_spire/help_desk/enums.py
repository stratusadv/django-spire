from enum import Enum


class TicketEventType(Enum):
    NEW = 'new'
    UPDATE = 'update'
    COMMENT = 'comment'
