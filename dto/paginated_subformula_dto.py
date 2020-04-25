import logging

from init import config

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class PaginatedSubFormulaDto:
    def __init__(self,
                 items,
                 has_prev,
                 has_next,
                 prev_num,
                 next_num,
                 page,
                 pages):
        self.items = items
        self.has_prev = has_prev
        self.has_next = has_next
        self.prev_num = prev_num
        self.next_num = next_num
        self.page = page
        self.pages = pages
        
