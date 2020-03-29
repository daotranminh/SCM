import logging

from init import config

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class DecorationTechniqueManager:
    def __init__(self, decoration_technique_repo):
        self.decoration_technique_repo = decoration_technique_repo

    def get_decoration_technique_choices(self):
        decoration_technique_recs = self.decoration_technique_repo.get_all_decoration_techniques()
        decoration_technique_choices = []
        for decoration_technique_rec in decoration_technique_recs:
            decoration_technique_choices.append((decoration_technique_rec.id, decoration_technique_rec.name))

        return decoration_technique_choices