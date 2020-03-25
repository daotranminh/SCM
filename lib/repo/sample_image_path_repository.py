import logging
import os

from flask import url_for
from flask_sqlalchemy import sqlalchemy
from werkzeug.utils import secure_filename

from sqlalchemy import desc

from init import SampleImagePath, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class SampleImagePathRepository:
    def __init__(self, db):
        self.db = db

    def get_sample_image_path(self,
                              sample_image_path_id):
        return SampleImagePath.query. \
            filter(SampleImagePath.id == sample_image_path_id). \
            first()

    def get_sample_image_paths(self,
                               sample_images_group_id):
        return SampleImagePath.query. \
            filter(SampleImagePath.sample_images_group_id == sample_images_group_id). \
            all()

    def get_latest_3_sample_image_paths(self,
                                       sample_images_group_id):
        sample_image_recs = self.db.session.query(SampleImagePath.file_path). \
            filter(SampleImagePath.sample_images_group_id == sample_images_group_id). \
            order_by(desc(SampleImagePath.uploaded_on)). \
            limit(3). \
            all()

        most_3_latest_sample_image_paths = []
        for sample_image_rec in sample_image_recs:
            most_3_latest_sample_image_paths.append(sample_image_rec.file_path)

        l = len(most_3_latest_sample_image_paths)
        if l < 3:
            for i in range(l, 3):
                most_3_latest_sample_image_paths.append('')

        return most_3_latest_sample_image_paths

    def add_sample_image_path(self,
                              sample_images_group_id,
                              file_path):
        try:
            sample_image_path_rec = SampleImagePath(sample_images_group_id=sample_images_group_id,
                                                    file_path=file_path)
            self.db.session.add(sample_image_path_rec)
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add sample_image_path record. Detail: %s' % (str(ex))
            logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_SAMPLE_IMAGE_PATH_FAILED, message)

    def delete_sample_image_paths(self,
                                  sample_images_group_id):
        sample_image_path_recs = self.get_sample_image_paths(sample_images_group_id)
        for sample_image_path_rec in sample_image_path_recs:
            self.delete_sample_image_path_rec(sample_image_path_rec)
        
    def delete_sample_image_path(self,
                                 sample_image_path_rec):
        try:
            if sample_image_path_rec is not None:
                filepath_for_deleting = os.path.join('init', sample_image_path_rec.file_path[1:])                
                self.db.session.delete(sample_image_path_rec)
                os.remove(filepath_for_deleting)
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to delete sample_image_path %s. Detail: %s' % (str(sample_image_path_id), str(ex))
            logger.error(message)
            raise ScmException(ErrorCodes.ERROR_DELETE_SAMPLE_IMAGE_PATH_FAILED, message)
                
                
