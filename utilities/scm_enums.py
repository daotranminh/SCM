from enum import IntEnum

class ErrorCodes(IntEnum):
    SUCCESS = 0
    ERROR_ADD_MATERIAL_FAILED = 1
    ERROR_ADD_MATERIAL_VERSION_FAILED = 2
    ERROR_ADD_CUSTOMER_FAILED = 3
    ERROR_ADD_TASTE_FAILED = 4
    ERROR_ADD_TOPIC_FAILED = 5
    ERROR_UPDATE_TOPIC_FAILED = 6
    ERROR_ADD_MATERIAL_FORMULA_FAILED = 7
    ERROR_ADD_FORMULA_FAILED = 8

class DecorationForms(IntEnum):
    ROUND = 0
    RECTANGLE = 1
    BOX = 2

class DecorationTechniques(IntEnum):
    SIMPLE = 0
    DRAWING = 1
    FONDANT = 2

class OrderStatus(IntEnum):
    PENDING = 0
    CANCELLED = 1
    DELIVERED_HOLDING_BOX = 2
    CLOSED = 3
