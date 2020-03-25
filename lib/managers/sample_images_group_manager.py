import logging
import os

from flask import url_for
from werkzeug.utils import secure_filename

from init import config

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class SampleImagesGroupManager:
    def __init__(self,
                 sample_images_group_repo,
                 sample_image_path_repo):
        self.sample_images_group_repo = sample_images_group_repo
        self.sample_image_path_repo = sample_image_path_repo

    def get_latest_groups_3_image_paths(self,
                                        sample_images_group_recs):
        latest_groups_3_image_paths = []
        for sample_images_group_rec in sample_images_group_recs:
            most_3_latest_sample_image_paths = self.sample_image_path_repo.get_latest_3_sample_image_paths(sample_images_group_rec.id)
            latest_groups_3_image_paths += most_3_latest_sample_image_paths

        return latest_groups_3_image_paths
        
    def add_sample_images_group(self,
                                topic_id,
                                uploaded_files):
        new_sample_images_group_id = self.sample_images_group_repo.add_sample_images_group(topic_id)

        for uploaded_file in uploaded_files:
            filename = str(new_sample_images_group_id) + '_' + secure_filename(uploaded_file.filename)
            filepath_for_saving = os.path.join('init/static', config['IMAGES_DB']['SAMPLE_IMAGES_FOLDER'], filename)
            uploaded_file.save(filepath_for_saving)

            filepath_for_db = url_for('static', filename=os.path.join(config['IMAGES_DB']['SAMPLE_IMAGES_FOLDER'], filename))
            self.sample_image_path_repo.add_sample_image_path(new_sample_images_group_id,
                                                              filepath_for_db)
        
    def delete_sample_images_group(self,
                                   sample_images_group_id):
        self.sample_image_path_repo.delete_sample_image_paths(sample_images_group_id)
        self.sample_images_group_repo.delete_sample_images_group(sample_images_group_id)
        

    
