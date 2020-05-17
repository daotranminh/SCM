import logging

from flask_sqlalchemy import sqlalchemy

from init import Material, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException
from utilities.scm_logger import ScmLogger

class MaterialRepository:
    logger = ScmLogger(__name__)

    def __init__(self, db):
        self.db = db

    def get_all_materials(self):
        return Material.query. \
            order_by(Material.name). \
            all()

    def get_paginated_materials(self,
                                page,
                                per_page,
                                search_text):
        material_recs = Material.query
        if search_text is not None and search_text != '':
            search_pattern = '%' + search_text + '%'
            material_recs = material_recs.filter(Material.name.ilike(search_pattern))

        material_recs = material_recs.order_by(Material.name)
        return material_recs.paginate(page, per_page, error_out=False)

    def get_material(self, id):
        return Material.query.filter(Material.id == id).first()

    def add_material(self,
                     name,
                     description,
                     is_organic,
                     unit_amount,
                     unit):
        try:
            material_rec = Material(name=name,
                                    description=description,
                                    is_organic=is_organic,
                                    unit_amount=unit_amount,
                                    unit=unit)
            self.db.session.add(material_rec)
            self.db.session.flush()
            return material_rec.id
        
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add material. Details: %s' % (str(ex))
            MaterialRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_MATERIAL_FAILED, message)

    
