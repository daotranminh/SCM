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
                 formula_type,
                 description,
                 note,
                 total_cost,
                 registered_on):
        self.formula_id = formula_id
        self.name = name
        self.formula_type = formula_type
        self.description = description
        self.note = note
        self.total_cost = total_cost
        self.registered_on = registered_on
        
