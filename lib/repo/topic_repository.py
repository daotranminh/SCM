import logging

from flask_sqlalchemy import sqlalchemy

from init import Topic, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException
from utilities.scm_logger import ScmLogger

class TopicRepository:
    logger = ScmLogger(__name__)

    def __init__(self, db):
        self.db = db

    def get_all_topics(self):
        return Topic.query. \
            order_by(Topic.name). \
            all()

    def get_topic(self, id):
        return Topic.query.filter(Topic.id == id).first()

    def add_topic(self,
                  name,
                  description,
                  parent_id):
        try:
            topic_rec = Topic(name=name,
                              description=description,
                              parent_id=parent_id)
            self.db.session.add(topic_rec)
            self.db.session.flush()
            return topic_rec.id
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add topic %s. Details: %s' % (name, str(ex))
            TopicRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_TOPIC_FAILED, message)

    def update_topic(self,
                     topic_id,
                     name,
                     description,
                     parent_id):
        if parent_id == topic_id:
            message = 'Topic %s cannot be its own parent' % topic_id
            TopicRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_UPDATE_TOPIC_FAILED, message)
        
        topic_rec = self.get_topic(topic_id)
        topic_rec.name = name
        topic_rec.description = description
        topic_rec.parent_id = parent_id
