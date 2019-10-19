from .scm_enums import DecorationForms
from .scm_enums import DecorationTechniques

UNIT_CHOICES = [('kg', 'kg'),
                ('l', 'l'),
                ('piece', 'piece')]

MENU_CONFIGURATION = 'menu_configuration'
MENU_CUSTOMER = 'customer_funcs'
MENU_STATISTICS = 'statistics_funcs'

DECORATION_FORMS = [(str(DecorationForms.ROUND), 'Round'),
                    (str(DecorationForms.RECTANGLE), 'Rectangle'),
                    (str(DecorationForms.BOX), 'Box')]

DECORATION_TECHNIQUES = [(str(DecorationTechniques.SIMPLE), 'Simple'),
                         (str(DecorationTechniques.DRAWING), 'Drawing'),
                         (str(DecorationTechniques.FONDANT), 'Fondant')]
