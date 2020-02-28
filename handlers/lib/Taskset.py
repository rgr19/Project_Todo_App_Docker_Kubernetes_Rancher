#!/usr/bin/env python3.7
import os

from handlers.lib.common import *

logger = logging.getLogger(__name__)

logger.info("Hello logging!")


class TasksetConfig(object):
    SRC: str = 'src'
    TASKSET: str = 'taskset'
    PROJECT_FORM: str = '{PROJECT_NAME}'
    FORM_PATH_SRC: str = os.path.join(PROJECT_FORM, SRC)
    FORM_PATH_TASKSET: str = os.path.join(PROJECT_FORM, TASKSET)
    TEMPORARY: str = 'temporary'
    TEMPLATE: str = 'template'
    reloadedTasks: set = set()
    GITHUB_USER: str = 'GITHUB_USER'
    GITHUB_BRANCH: str = 'GITHUB_BRANCH'

    def __init__(self, PROJECT_NAME, BUILD_TYPE, DIR_ENVFILES, DIR_SECRETFILES, PROJECT_VERSION, **_):
        logger.info(f'{__class__.__name__}.__init__')

        self.PROJECT_NAME: str = PROJECT_NAME
        self.BUILD_TYPE: str = BUILD_TYPE
        self.DIR_ENVFILES: str = DIR_ENVFILES
        self.DIR_SECRETFILES: str = DIR_SECRETFILES
        self.PROJECT_VERSION: str = PROJECT_VERSION
        self.PATH_CODE_SRC: str = os.path.join(PROJECT_NAME, 'src')
        self.PATH_TASKSET: str = os.path.join(PROJECT_NAME, 'taskset')

        self.GITHUB_BRANCH_ENVFILE: str = os.path.join(DIR_ENVFILES, self.GITHUB_BRANCH)
        self.GITHUB_USER_ENVFILE: str = os.path.join(DIR_ENVFILES, self.GITHUB_USER)

    def is_reloaded(self):
        if self.__class__.__name__ in self.reloadedTasks:
            return True
        self.reloadedTasks.add(self.__class__.__name__)
        return False
