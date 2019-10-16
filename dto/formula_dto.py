import logging

from init import config

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class FormulaDto:
    def __init__(self,
                 formula_id,
                 name,
                 taste,
                 description,
                 registered_on):
        self.formula_id = formula_id
        self.name = name
        self.taste = taste
        self.description = description
        self.registered_on = registered_on
        
