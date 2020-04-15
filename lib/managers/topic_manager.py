import logging

from init import config
from dto.topic_dto import TopicDto
from utilities.scm_logger import ScmLogger

class TopicManager:
    logger = ScmLogger(__name__)

    def __init__(self, topic_repo):
        self.topic_repo = topic_repo

    def get_topic_choices(self):
        topic_recs = self.topic_repo.get_all_topics()

        topic_choices = [(-1, '')]
        for topic_rec in topic_recs:
            topic_choices.append((topic_rec.id, topic_rec.name))

        return topic_choices

    def get_topic_dtos(self):
        topic_recs = self.topic_repo.get_all_topics()
        topics_dict = {}

        for topic_rec in topic_recs:
            topics_dict[topic_rec.id] = topic_rec

        topic_dtos = []
        for topic_rec in topic_recs:
            parent_name = ''
            if topic_rec.parent_id != -1:
                parent_name = topics_dict[topic_rec.parent_id].name
            topic_dto = TopicDto(topic_rec.id,
                                 topic_rec.name,
                                 topic_rec.description,
                                 topic_rec.parent_id,
                                 parent_name)
            topic_dtos.append(topic_dto)
        return topic_dtos
