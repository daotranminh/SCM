import logging

from flask import url_for

from init import config
from utilities.scm_logger import ScmLogger

class SampleImagesGroupManager:
    logger = ScmLogger(__name__)

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
                                sample_images_group_name,
                                uploaded_files):
        new_sample_images_group_id = self.sample_images_group_repo.add_sample_images_group(topic_id,
                                                                                           sample_images_group_name)
        self.sample_image_path_repo.add_sample_image_paths(new_sample_images_group_id,
                                                           uploaded_files)
        
    def delete_sample_images_group(self,
                                   sample_images_group_id):
        self.sample_image_path_repo.delete_sample_image_paths(sample_images_group_id)
        self.sample_images_group_repo.delete_sample_images_group(sample_images_group_id)
        
    def update_sample_images_group(self,
                                   sample_images_group_id,
                                   topic_id,
                                   sample_images_group_name,
                                   sample_image_path_recs,
                                   remaining_sample_image_path_ids,
                                   uploaded_files):
        self.sample_images_group_repo.update_sample_images_group(sample_images_group_id,
                                                                 topic_id,
                                                                 sample_images_group_name)
            
        self.sample_image_path_repo.update_sample_image_paths(sample_images_group_id,
                                                              sample_image_path_recs,
                                                              remaining_sample_image_path_ids,
                                                              uploaded_files)
    
