import logging

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

    def delete_sample_images_group(self,
                                   sample_images_group_id):
        self.sample_image_path_repo.delete_sample_image_paths(sample_images_group_id)
        self.sample_images_group_repo.delete_sample_images_group(sample_images_group_id)
        

    
