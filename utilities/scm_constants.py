from .scm_enums import OrderStatus

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