from .scm_enums import OrderStatus, PaymentStatus, BoxStatus, SubFormulaTypes

UNIT_CHOICES = ['g', 'ml', 'kg', 'l', 'piece']

MENU_CONFIGURATION = 'menu_configuration'
MENU_CUSTOMER = 'customer_funcs'
MENU_STATISTICS = 'statistics_funcs'

ORDER_STATUS_NAMES = [(int(OrderStatus.PENDING), 'Pending'),
                      (int(OrderStatus.IN_PRODUCTION), 'In Production'),
                      (int(OrderStatus.DELIVERED), 'Delivered')]

PAYMENT_STATUS_NAMES = [(int(PaymentStatus.NOT_PAID), 'Not paid'),
                        (int(PaymentStatus.PARTLY_PAID), 'Partly paid'),
                        (int(PaymentStatus.FULLY_PAID), 'Fully paid')]

BOX_STATUS_NAMES = [(int(BoxStatus.BOX_NOT_NEEDED_TO_BE_RETURNED), 'Box not needed'),
                    (int(BoxStatus.BOX_WITH_PRODUCT_IN_PRODUCTION), 'Box with product in production'),
                    (int(BoxStatus.BOX_AT_CUSTOMER_AFTER_DELIVERY), 'Box at customer after delivery'),
                    (int(BoxStatus.BOX_RETURNED), 'Box returned')]

FORMULA_TYPE_NAMES = [(int(SubFormulaTypes.BASE), 'Base'),
                      (int(SubFormulaTypes.FILLING), 'Filling'),
                      (int(SubFormulaTypes.CREAM), 'Cream')]
