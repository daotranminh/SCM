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
    ERROR_ADD_DECORATIONFAILED = 9
    ERROR_ADD_DECORATION_FORM_FAILED = 10
    ERROR_ADD_DECORATION_TECHNIQUE_FAILED = 11
    ERROR_ADD_DECORATION_TEMPLATE_PATH_FAILED = 12
    ERROR_ADD_ORDER_FAILED = 13
    ERROR_ADD_SAMPLE_IMAGE_PATH_FAILED = 14
    ERROR_DELETE_SAMPLE_IMAGE_PATH_FAILED = 15
    ERROR_ADD_SAMPLE_IMAGES_GROUP_FAILED = 16
    ERROR_DELETE_SAMPLE_IMAGES_GROUP_FAILED = 17
    ERROR_ADD_PRODUCT_FAILED = 18
    ERROR_ADD_PRODUCT_IMAGE_PATH_FAILED = 19
    ERROR_DELETE_PRODUCT_FAILED = 20
    ERROR_ADD_ORDER_STATUS_FAILED = 21

class PaymentStatus(IntEnum):
    NOT_PAID = 0
    PARTLY_PAID = 1
    FULLY_PAID = 2

class BoxStatus(IntEnum):
    BOX_NOT_NEEDED = 0
    BOX_WITH_PRODUCT_IN_PRODUCTION = 1
    BOX_AT_CUSTOMER_AFTER_DELIVERY = 2
    BOX_RETURNED = 3

class OrderStatus(IntEnum):
    PENDING = 0
    IN_PRODUCTION = 1
    DELIVERED = 2
