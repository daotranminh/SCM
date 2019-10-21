import logging

from init import config

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class DecorationDto:
    def __init__(self,
                 decoration_id,
                 name,
                 description,
                 topic,
                 decoration_form,
                 decoration_technique):
        self.decoration_id = decoration_id
        self.name = name
        self.description = description
        self.topic = topic
        self.decoration_form = decoration_form
        self.decoration_technique = decoration_technique
        
