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
                 material_id,
                 name,
                 description,
                 is_organic,
                 unit,
                 material_version_id,
                 unit_price):
        self.material_id = material_id
        self.name = name
        self.description = description
        self.is_organic = is_organic
        self.unit = unit
        self.material_version_id = material_version_id
        self.unit_price = unit_price

class MaterialFormulaDto(MaterialDto):
    def __init__(self,
                 material_id,
                 name,
                 description,
                 is_organic,
                 unit,
                 material_version_id,
                 unit_price,
                 amount):
        super(MaterialFormulaDto, self).__init__(material_id,
                                                 name,
                                                 description,
                                                 is_organic,
                                                 unit,
                                                 material_version_id,
                                                 unit_price)
        self.amount = amount
