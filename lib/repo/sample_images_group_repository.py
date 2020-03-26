import logging
import os

from flask import url_for
from flask_sqlalchemy import sqlalchemy
from werkzeug.utils import secure_filename

from init import SampleImagesGroup, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class SampleImagesGroupRepository:
    def __init__(self, db):
        self.db = db

    def get_sample_images_group(self,
                                sample_images_group_id):
        return SampleImagesGroup.query. \
            filter(SampleImagesGroup.id == sample_images_group_id). \
            first()

    def get_sample_images_groups_by_topic(self,
                                          topic_id):
        return SampleImagesGroup.query. \
            filter(SampleImagesGroup.topic_id == topic_id). \
            all()

    def update_sample_images_group(self,
                                   sample_images_group_id,
                                   topic_id,
                                   sample_images_group_name):
        sample_images_group_rec = self.get_sample_images_group(sample_images_group_id)
        if sample_images_group_rec is not None:
            sample_images_group_rec.topic_id = topic_id
            sample_images_group_rec.name = sample_images_group_name
    
    def add_sample_images_group(self,
                                topic_id,
                                sample_images_group_name):
        try:
            sample_images_group_rec = SampleImagesGroup(topic_id=topic_id,
                                                        name=sample_images_group_name)
            self.db.session.add(sample_images_group_rec)
            self.db.session.flush()
            return sample_images_group_rec.id
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add sample_images_group record. Detail: %s' % (str(ex))
            logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_SAMPLE_IMAGES_GROUP_FAILED, message)

    def delete_sample_images_group(self,
                                   sample_images_group_id):
        try:
            sample_images_group_rec = self.get_sample_images_group(sample_images_group_id)
            if sample_images_group_rec is not None:
                self.db.session.delete(sample_images_group_rec)
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to delete sample_images_group %s. Detail: %s' % (str(sample_images_group_id), str(ex))
            logger.error(message)
            raise ScmException(ErrorCodes.ERROR_DELETE_SAMPLE_IMAGES_GROUP_FAILED, message)
                
                
