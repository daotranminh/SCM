import logging

from init import config

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class MaterialDto:
    def __init__(self,
                 name,
                 description,
                 is_organic,
                 unit,
                 unit_price):
        self.name = name
        self.description = description
        self.is_organic = is_organic
        self.unit = unit
        self.unit_price = unit_price
