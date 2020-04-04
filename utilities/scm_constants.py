from .scm_enums import OrderStatus, PaymentStatus

UNIT_CHOICES = [('g', 'g'),
                ('ml', 'ml'),
                ('kg', 'kg'),
                ('l', 'l'),
                ('piece', 'piece')]

MENU_CONFIGURATION = 'menu_configuration'
MENU_CUSTOMER = 'customer_funcs'
MENU_STATISTICS = 'statistics_funcs'

ORDER_STATUS_NAMES = [(int(OrderStatus.PENDING), 'Pending'),
                      (int(OrderStatus.IN_PRODUCTION), 'In Production'),
                      (int(OrderStatus.DELIVERED), 'Delivered')]

PAYMENT_STATUS_NAMES = [(int(PaymentStatus.NOT_PAID), 'Not paid'),
                        (int(PaymentStatus.PARTLY_PAID), 'Partly paid'),
                        (int(PaymentStatus.FULLY_PAID), 'Fully paid')
]