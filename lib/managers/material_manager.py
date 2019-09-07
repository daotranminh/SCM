import logging

from init import config

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class MaterialManager:
    def __init__(self,
                 material_repo,
                 material_version_repo):
        self.material_repo = material_repo
        self.material_version_repo = material_version_repo

    def add_material(self,
                     name,
                     description,
                     is_organic,
                     unit,
                     unit_price):
        message = 'name=%s, unit=%s, unit_price=%s' % (name,
                                                       unit,
                                                       unit_price)
        print(message)
        logger.debug(message)
        new_material_id = self.material_repo.add_material(name,
                                                          description,
                                                          is_organic,
                                                          unit)

        message = 'new_material_id=%s' % new_material_id
        logger.debug(message)
        self.material_version_repo.add_material_version(new_material_id,
                                                        unit_price)
