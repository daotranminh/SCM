import logging

from flask_sqlalchemy import sqlalchemy

from init import Topic, config
from utilities.scm_exceptions import ScmException

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class TopicRepository:
    def __init__(self, db):
        self.db = db

    def get_all_topics(self):
        return Topic.query.all()

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
            logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_TOPIC_FAILED, message)

    def update_taste(self,
                     topic_id,
                     name,
                     description,
                     parent_id):
        topic_rec = self.get_taste(topic_id)
        topic_rec.name = name
        topic_rec.description = description
        topic_rec.parent_id = parent_id
