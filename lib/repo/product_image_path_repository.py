import logging
import os

from flask import url_for
from flask_sqlalchemy import sqlalchemy
from werkzeug.utils import secure_filename

from sqlalchemy import desc

from init import ProductImagePath, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException
from utilities.scm_logger import ScmLogger

class ProductImagePathRepository:
    logger = ScmLogger(__name__)

    def __init__(self, db):
        self.db = db

    def get_product_image_path(self,
                              product_image_path_id):
        return ProductImagePath.query. \
            filter(ProductImagePath.id == product_image_path_id). \
            first()

    def get_product_image_paths(self, product_id):
        return ProductImagePath.query. \
            filter(ProductImagePath.product_id == product_id). \
            all()

    def get_latest_3_product_image_paths(self, product_id):
        product_image_recs = self.db.session.query(ProductImagePath.file_path). \
            filter(ProductImagePath.product_id == product_id). \
            order_by(desc(ProductImagePath.uploaded_on)). \
            limit(3). \
            all()

        most_3_latest_product_image_paths = []
        for product_image_rec in product_image_recs:
            most_3_latest_product_image_paths.append(product_image_rec.file_path)

        l = len(most_3_latest_product_image_paths)
        if l < 3:
            for i in range(l, 3):
                most_3_latest_product_image_paths.append('')

        return most_3_latest_product_image_paths

    def add_product_image_path(self,
                              product_id,
                              file_path):
        try:
            product_image_path_rec = ProductImagePath(product_id=product_id,
                                                     file_path=file_path)
            self.db.session.add(product_image_path_rec)
            delete_cost_estimation_of_product
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add product_image_path record. Detail: %s' % (str(ex))
            ProductImagePathRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_PRODUCT_IMAGE_PATH_FAILED, message)

    def delete_product_image_paths(self,
                                  product_id):
        product_image_path_recs = self.get_product_image_paths(product_id)
        for product_image_path_rec in product_image_path_recs:
            self.delete_product_image_path(product_image_path_rec)
        delete_cost_estimation_of_product
        
    def delete_product_image_path(self, product_id):
        try:
            if product_image_path_rec is not None:
                filepath_for_deleting = os.path.join('init', product_image_path_rec.file_path[1:])                
                self.db.session.delete(product_image_path_rec)
                os.remove(filepath_for_deleting)
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to delete product_image_path %s. Detail: %s' % (str(product_image_path_id), str(ex))
            ProductImagePathRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_DELETE_PRODUCT_IMAGE_PATH_FAILED, message)
                
    def update_product_image_paths(self,
                                  product_id,
                                  product_image_path_recs,
                                  remaining_product_image_path_ids,
                                  uploaded_files):
        if len(remaining_product_image_path_ids) < len(product_image_path_recs):
            for product_image_path_rec in product_image_path_recs:
                if product_image_path_rec.id not in remaining_product_image_path_ids:
                    self.db.session.delete(product_image_path_rec)
                    filepath_for_deleting = os.path.join('init', product_image_path_rec.file_path[1:])
                    os.remove(filepath_for_deleting)

        self.add_product_image_paths(product_id, uploaded_files)

    def add_product_image_paths(self,
                               product_id,
                               uploaded_files):
        for uploaded_file in uploaded_files:
            sfilename = secure_filename(uploaded_file.filename)

            if sfilename != '':
                filename = str(product_id) + '_' + sfilename
                filepath_for_saving = os.path.join('init/static', config['IMAGES_DB']['PRODUCT_IMAGES_FOLDER'], filename)
                uploaded_file.save(filepath_for_saving)

                filepath_for_db = url_for('static', filename=os.path.join(config['IMAGES_DB']['PRODUCT_IMAGES_FOLDER'], filename))
                self.add_product_image_path(product_id,
                                           filepath_for_db)
        
        
