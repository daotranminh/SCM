import logging

from init import config

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class TasteManager:
    def __init__(self, taste_repo):
        self.taste_repo = taste_repo

    def get_taste_choices(self):
        taste_recs = self.taste_repo.get_all_tastes()
        taste_choices = []
        for taste_rec in taste_recs:
            taste_choices.append((taste_rec.id, taste_rec.name))

        return taste_choices
