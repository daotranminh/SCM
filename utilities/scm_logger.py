import os
import inspect
import logging

from init import config

class ScmLogger:
    def __init__(self,
                 logger_name,
                 log_function_name=True):
        self.logger = logging.getLogger(logger_name)
        self.handler = logging.FileHandler(config['DEFAULT']['log_file'])
        self.formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.INFO)

        self.log_function_name = log_function_name

    def __build_full_message(self, message):
        message_elements = []

        if self.log_function_name:
            message_elements.append('CALLER: ' + inspect.currentframe().f_back.f_back.f_code.co_name)

        message_elements.append(message)

        full_message = ' '.join(message_elements)
        return full_message

    def info(self, message):
        full_message = self.__build_full_message(message)
        self.logger.info(full_message)

    def debug(self, message):
        full_message = self.__build_full_message(message)
        self.logger.debug(full_message)

    def warning(self, message):
        full_message = self.__build_full_message(message)
        self.logger.warning(full_message)

    def error(self, message):
        full_message = self.__build_full_message(message)
        self.logger.error(full_message)

    def exception(self, ex):
        self.logger.exception(ex)