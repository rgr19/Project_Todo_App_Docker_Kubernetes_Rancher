#!/usr/bin/env python3.7
import os
from pprint import pprint

from handlers.lib.Logger import Logger

logger = Logger.build(__name__)


class TasksetConfig(object):
	SRC: str = 'src'
	TASKSET: str = 'taskset'
	PROJECT_FORM: str = '{PROJECT_NAME}'
	FORM_PATH_SRC: str = os.path.join(PROJECT_FORM, SRC)
	FORM_PATH_TASKSET: str = os.path.join(PROJECT_FORM, TASKSET)
	TEMPORARY: str = 'temporary'
	TEMPLATE: str = 'template'
	DATA: str = 'data'
	GITHUB_USER: str = 'GITHUB_USER'
	GITHUB_BRANCH: str = 'GITHUB_BRANCH'
	HELM_VERSION: str = 'HELM_VERSION'
	KUBECTL_VERSION: str = 'KUBECTL_VERSION'
	tasksetConfigMap: dict = dict()
	reloadedTasks: set = set()

	def __init__(self, RUNTIME_TYPE='NONE', PROJECT_NAME='project', PROJECT_VERSION='0.0.0', IMAGES_VERSION='0.0', BUILD_TYPE='prod', DIR_ENVFILES='.envfiles', DIR_SECRETFILES='.secretfiles', **_):
		logger.info(f'{__class__.__name__}.__init__')

		self.PROJECT_NAME: str = PROJECT_NAME
		self.BUILD_TYPE: str = BUILD_TYPE
		self.RUNTIME_TYPE: str = RUNTIME_TYPE
		self.DIR_ENVFILES: str = DIR_ENVFILES
		self.DIR_SECRETFILES: str = DIR_SECRETFILES
		self.PROJECT_VERSION: str = PROJECT_VERSION
		self.IMAGES_VERSION: str = IMAGES_VERSION
		self.PATH_CODE_SRC: str = os.path.join(PROJECT_NAME, 'src')
		self.PATH_TASKSET: str = os.path.join(PROJECT_NAME, 'taskset')

		self.GITHUB_BRANCH_ENVFILE: str = os.path.join(DIR_ENVFILES, self.GITHUB_BRANCH)
		self.GITHUB_USER_ENVFILE: str = os.path.join(DIR_ENVFILES, self.GITHUB_USER)
		self.HELM_VERSION: str = os.path.join(DIR_ENVFILES, self.HELM_VERSION)
		self.KUBECTL_VERSION: str = os.path.join(DIR_ENVFILES, self.KUBECTL_VERSION)

		self.tasksetConfigMap['PROJECT_NAME'] = PROJECT_NAME
		self.tasksetConfigMap['PROJECT_VERSION'] = PROJECT_VERSION
		self.tasksetConfigMap['IMAGES_VERSION'] = IMAGES_VERSION
		self.tasksetConfigMap['BUILD_TYPE'] = BUILD_TYPE
		self.tasksetConfigMap['RUNTIME_TYPE'] = RUNTIME_TYPE

		if not any(self.reloadedTasks):
			logger.info(f'{__class__.__name__}.__init__ TASKSET CONFIG :')
			pprint(self.tasksetConfigMap)

	def is_reloaded(self):
		logger.debug(f'{__class__.__name__}.is_reloaded')
		if self.__class__.__name__ in self.reloadedTasks:
			return True
		self.reloadedTasks.add(self.__class__.__name__)
		return False
