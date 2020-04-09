import logging

from init import config

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class MaterialCostEstimationDto:
    def __init__(self,
                 material_version_cost_estimation_id,
                 material_id,
                 material_verion_id,
                 cost_estimation_id,
                 unit_amount,
                 unit,
                 unit_price,
                 amount,
                 cost,
                 material_name):
        self.material_version_cost_estimation_id = material_version_cost_estimation_id
        self.material_id = material_id
        self.material_verion_id = material_verion_id
        self.cost_estimation_id = cost_estimation_id
        self.unit_amount = unit_amount
        self.unit = unit
        self.unit_price = unit_price
        self.amount = amount
        self.cost = cost
        self.material_name = material_name