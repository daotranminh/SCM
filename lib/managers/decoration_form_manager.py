import logging

from init import config

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class DecorationFormManager:
    def __init__(self, decoration_form_repo):
        self.decoration_form_repo = decoration_form_repo

    def get_decoration_form_choices(self):
        decoration_form_recs = self.decoration_form_repo.get_all_decoration_forms()
        decoration_form_choices = []
        for decoration_form_rec in decoration_form_recs:
            decoration_form_choices.append((decoration_form_rec.id, decoration_form_rec.name))

        return decoration_form_choices