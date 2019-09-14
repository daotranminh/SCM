import logging

from init import config

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class TopicDto:
    def __init__(self,
                 topic_id,
                 name,
                 description,
                 parent_topic_id,
                 parent_topic_name):
        self.topic_id = topic_id
        self.name = name
        self.description = description
        self.parent_topic_id = parent_topic_id
        self.parent_topic_name = parent_topic_name
        
