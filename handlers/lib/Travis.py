#!/usr/bin/env python3.7.7
import abc
import os
from shutil import copyfile
from typing import Type

from handlers.lib.Executor import Executor, ExecutorAbstract
from handlers.lib.FilesHandlers import YamlConcatWrite, EnvRead, Env, FileWrite
from handlers.lib.Git import GitExecutor
from handlers.lib.Logger import Logger
from handlers.lib.Taskset import TasksetConfig

logger = Logger.build(__name__)


class TravisTasks(object):
	class Abstract(abc.ABC):

		@property
		@abc.abstractmethod
		def TASK_MODE(self):
			pass

		@property
		@abc.abstractmethod
		def SECRETS(self):
			pass

		@property
		@abc.abstractmethod
		def TRAVIS_YML(self):
			pass

		@abc.abstractmethod
		def ROOT(self):
			pass

	class Base(Abstract):
		TASK_MODE = 'basic'

		SECRETS: set = {
			'DOCKER_HUB_PASSWORD',
			'DOCKER_HUB_ID',
			'GITHUB_BRANCH',
			'GITHUB_USER',
			'BUILD_TYPE',
		}

		TRAVIS_YML: str = f'root/.travis.{TASK_MODE}.yml'

	class Aws(Abstract):
		TASK_MODE: str = 'aws'
		SECRETS: set = {
			'AWS_SECRET_KEY',
			'AWS_KEY_ID'
		}
		TRAVIS_YML: str = f'root/.travis.{TASK_MODE}.yml'

	class HelmRepo(Abstract):
		TASK_MODE = 'helm'
		SECRETS: set = {
			'GITHUB_PAGES_URL',
			'HELM_VERSION',
			'KUBECTL_VERSION',
			'GITHUB_TOKEN',
		}

		TRAVIS_YML: str = f'submodules/.travis.{TASK_MODE}.yml'


class TravisConfigurator(TasksetConfig):
	# TODO: split travis for root and submodules
	# TODO: use separate repositories for docker images

	TRAVIS: str = 'travis'
	TRAVIS_YML: str = '.travis.yml'

	TASK_MAP: dict = dict(
		AWS=TravisTasks.Aws,
		BASE=TravisTasks.Base,
		HELM=TravisTasks.HelmRepo
	)

	ROOT = '.'

	def __init__(self, *tasks: Type[TravisTasks.Abstract], destPath: str = None, **configurationVariables):
		logger.info(f'{__class__.__name__}.__init__')
		super().__init__(**configurationVariables)

		self.taskPath: str = os.path.join(self.PATH_TASKSET, self.TRAVIS)
		self.templatePath: str = os.path.join(self.taskPath, self.TEMPLATE)
		self.travisYmlPath: str = os.path.join(self.taskPath, self.TRAVIS_YML)

		if destPath:
			assert (os.path.exists(destPath))

		self.cwdPath: str = self.taskPath
		self.destPath: str = self.ROOT if destPath is None else destPath

		assert (t in self.TASK_MAP.values() for t in tasks)

		self.tasksList: tuple = tasks
		self.tasksNames: str = ' '.join([t.TASK_MODE for t in self.tasksList])
		self.taskYamlsUsed: list = []
		self.envVarsSecrets: list = []

		os.makedirs(self.taskPath, exist_ok=True)
		os.makedirs(self.templatePath, exist_ok=True)

	def save_github_config_to_envfiles(self, **configurationKwargs):
		logger.debug(f'{__class__.__name__}.save_github_config_to_envfiles')
		if not configurationKwargs:
			logger.exception("Dict of `configurationKwargs` can not be empty.")
		gitBranch = GitExecutor().branch()
		gitUserName = GitExecutor().user_name()
		FileWrite(self.GITHUB_BRANCH_ENVFILE, gitBranch)
		FileWrite(self.GITHUB_USER_ENVFILE, gitUserName)
		return self

	def merge_travis_templates(self):
		logger.debug(f'{__class__.__name__}.merge_travis_templates_to')

		destTravisYml = os.path.join(self.destPath, self.TRAVIS_YML)

		for task in self.tasksList:
			templateTravisAwsYml = os.path.join(self.templatePath, task.TRAVIS_YML)
			self.taskYamlsUsed.append(templateTravisAwsYml)

		YamlConcatWrite.as_is(self.travisYmlPath, *self.taskYamlsUsed)
		copyfile(self.travisYmlPath, destTravisYml)
		return self

	def load_envvars_and_secrets(self, *customSecrets: str):
		logger.debug(f'{__class__.__name__}.load_envvars_and_secrets')

		allSecrets = {}
		allSecrets.update(EnvRead.dir_to_dict(self.DIR_SECRETFILES))
		allSecrets.update(EnvRead.dir_to_dict(self.DIR_ENVFILES))

		for secret in customSecrets:
			k, v = secret.split('=')
			allSecrets[k] = v

		tasksSecrets = dict()
		for task in self.tasksList:
			for k in task.SECRETS:
				tasksSecrets[k] = allSecrets[k]

		self.envVarsSecrets = Env.dict_to_env_lines(tasksSecrets)

		return self

	@staticmethod
	def main(destPath: str = None, DO_RELOAD: str = True, **configurationKwargs):
		logger.debug(f'{__class__.__name__}.main')

		travis: TravisConfigurator = TravisConfigurator(destPath=destPath, **configurationKwargs)

		if DO_RELOAD:
			if travis.is_reloaded():
				return travis

			travis.save_github_config_to_envfiles(**configurationKwargs)

		TravisExecutor(destPath=destPath, **configurationKwargs).enable()

		return travis


class TravisKeys:
	TRAVIS: str = 'travis'
	ENCRYPT: str = 'encrypt'
	ENABLE: str = 'enable'
	ADD: str = 'add'
	ENV_GLOBAL: str = 'env.global'
	OVERRIDE: str = 'override'
	ORG: str = 'org'
	LOGS: str = 'logs'


class TravisExecutor(ExecutorAbstract, TravisConfigurator):

	# TODO: .git/config need to have `[travis] slug = rgr19/todo-app` matching with origin
	# todo: otherwise we will have exception repository not known to https://api.travis-ci.org/: <account>/<bad_origin_url>

	def __call__(self, subcommand: str = None) -> Executor:
		logger.debug(f'{__class__.__name__}.__call__ => {TravisKeys.TRAVIS} {subcommand} with CWD {self.cwdPath} ')
		return Executor(TravisKeys.TRAVIS).with_cwd(self.cwdPath).with_subcommand(subcommand)

	def encrypt(self, *secrets):
		logger.debug(f'{__class__.__name__}.encrypt')
		self(TravisKeys.ENCRYPT).with_args(*secrets).with_kwarg(TravisKeys.ADD, TravisKeys.ENV_GLOBAL).with_flags(TravisKeys.OVERRIDE, TravisKeys.ORG).spawn()

	def logs(self, *secrets):
		logger.debug(f'{__class__.__name__}.logs')
		self(TravisKeys.LOGS).with_args(*secrets).with_flags(TravisKeys.ORG).spawn(doUntilOk=True, exitOnError=False)

	def enable(self):
		logger.debug(f'{__class__.__name__}.enable')
		self(TravisKeys.ENABLE).with_flags(TravisKeys.ORG).spawn()

	def basic_task(self, gitMessage: str, *secrets: str):
		logger.debug(f'{__class__.__name__}.basic')
		self.task(gitMessage, *secrets)

	def aws_task(self, gitMessage: str, *secrets: str):
		logger.debug(f'{__class__.__name__}.aws')
		self.task(gitMessage, *secrets)

	def task(self, gitMessage: str, *secrets: str):
		logger.debug(f'{__class__.__name__}.task')
		self.merge_travis_templates()
		self.load_envvars_and_secrets(*secrets)
		self.encrypt(*self.envVarsSecrets, )
		if not gitMessage:
			gitMessage = f"Travis AUTO commit in MODE {self.tasksNames}"
		GitExecutor(self.cwdPath).upload(gitMessage)


class TravisSubmoduleExecutor(TravisExecutor, TravisConfigurator):

	def __call__(self, subcommand: str = None) -> Executor:
		logger.debug(f'{__class__.__name__}.__call__ => {self.TRAVIS} {subcommand} with CWD {self.destPath} ')
		return Executor(self.TRAVIS).with_cwd(self.destPath).with_subcommand(subcommand)

	def helm(self, gitMessage: str, *secrets: str):
		logger.debug(f'{__class__.__name__}.helm')
		self.task(gitMessage, *secrets)

	def task(self, gitMessage: str, *secrets: str):
		logger.debug(f'{__class__.__name__}.task')
		self.merge_travis_templates()
		self.load_envvars_and_secrets(*secrets)
		self.encrypt(*self.envVarsSecrets, )
		if not gitMessage:
			gitMessage = f"Travis AUTO commit in MODE {self.tasksNames}"
		GitExecutor(self.destPath).upload(gitMessage)
