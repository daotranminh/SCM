import logging

from init import config

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class SubFormulaDto:
    def __init__(self,
                 subformula_id,
                 name,
                 subformula_type,
                 description,
                 note,
                 total_cost,
                 registered_on):
        self.subformula_id = subformula_id
        self.name = name
        self.subformula_type = subformula_type
        self.description = description
        self.note = note
        self.total_cost = total_cost
        self.registered_on = registered_on
        
