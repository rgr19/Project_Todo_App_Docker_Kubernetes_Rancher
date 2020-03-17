#!/usr/bin/env python3.7.7
import os
from shutil import copyfile

from handlers.lib.Executor import Executor, ExecutorAbstract
from handlers.lib.FilesHandlers import YamlWrite, EnvRead, EnvWrite, FileExpandvarsWrite, Env, FileRead, FileWrite
from handlers.lib.Helm import HelmConfigurator
from handlers.lib.Logger import Logger
from handlers.lib.MemoryConverter import MEMORY_STRING, MemoryConverter
from handlers.lib.Taskset import TasksetConfig

logger = Logger.build(__name__)


class DockerKeys:
	DOCKER: str = 'docker'
	DOCKER_COMPOSE: str = 'docker-compose'
	BUILD: str = 'build'
	UP: str = 'up'
	DOWN: str = 'down'
	KILL: str = 'kill'
	PULL: str = 'pull'
	PUSH: str = 'push'
	LOGS: str = 'logs'

	PARALLEL: str = 'parallel'
	VOLUMES: str = 'volumes'
	REMOVE_ORPHANS: str = 'remove-orphans'
	FORCE_RECREATE: str = 'force-recreate'
	DETACH: str = 'detach'
	ABORT_ON_CONTAINER_EXIT: str = 'abort-on-container-exit'
	RENEW_ANON_VOLUMES: str = 'renew-anon-volumes'
	PROJECT_DIRECTORY: str = 'project-directory'
	PROJECT_NAME: str = 'project-name'
	TIMESTAMPS: str = 'timestamps'
	FOLLOW: str = 'follow'


class DockerComposeConfigurator(TasksetConfig):
	PROD: str = 'prod'
	DEV: str = 'dev'
	TEMPLATE: str = 'template'
	TEMP_DIR: str = 'temporary'
	ENV_FILE: str = '.env'
	ENV_HELM_FILE: str = ENV_FILE + '.helm'
	ENV_DOCKER_COMPOSE_FILE: str = ENV_FILE + '.dc'

	DOCKER_COMPOSE_VERSION = 'DOCKER_COMPOSE_VERSION'

	YAML_DOCKER_COMPOSE = 'docker-compose.yaml'
	YAML_DOCKER_COMPOSE_LIMITS = 'docker-compose.limits.yaml'
	YAML_DOCKER_COMPOSE_OVERRIDE = 'docker-compose.override.yaml'

	DEV_YAMLS: list = [
		YAML_DOCKER_COMPOSE,
		YAML_DOCKER_COMPOSE_LIMITS
	]

	PROD_YAMLS: list = DEV_YAMLS + [
		YAML_DOCKER_COMPOSE_OVERRIDE
	]

	def __init__(self, **configurationVariables):
		logger.debug(f'{__class__.__name__}.__init__')
		super().__init__(RUNTIME_TYPE=DockerKeys.DOCKER_COMPOSE, **configurationVariables)

		self.taskPath = os.path.join(self.PATH_TASKSET, DockerKeys.DOCKER)
		self.prodPath = os.path.join(self.taskPath, self.PROD)
		self.devPath = os.path.join(self.taskPath, self.DEV)
		self.templatePath = os.path.join(self.taskPath, self.TEMPLATE)

		if self.BUILD_TYPE == self.PROD:
			self.cwdPath = self.prodPath
			self.buildYamls = self.PROD_YAMLS
		elif self.BUILD_TYPE == self.DEV:
			self.cwdPath = self.devPath
			self.buildYamls = self.DEV_YAMLS
		else:
			raise ValueError("BUILD_TYPE has to be one of {prod, dev}")

		self.tempPath = os.path.join(self.cwdPath, self.TEMP_DIR)
		self.envFilePath = os.path.join(self.cwdPath, self.ENV_FILE)
		self.envHelmFilePath = os.path.join(self.cwdPath, self.ENV_HELM_FILE)
		self.envDockerComposeFilePath = os.path.join(self.cwdPath, self.ENV_DOCKER_COMPOSE_FILE)

		if self.YAML_DOCKER_COMPOSE_LIMITS in self.buildYamls:
			self.dockerComposeVersion = "2.2"
		else:
			self.dockerComposeVersion = "3.7"

		os.makedirs(self.taskPath, exist_ok=True)
		os.makedirs(self.cwdPath, exist_ok=True)
		os.makedirs(self.tempPath, exist_ok=True)

	def copy_helm_values_as_env_helm(self, yamlPath: str):
		logger.debug(f'{__class__.__name__}.copy_helm_values_as_env')
		YamlWrite.as_env(yamlPath, self.envHelmFilePath)

	def fix_memory_format_in_env_helm(self):
		logger.debug(f'{__class__.__name__}.fix_memory_format_in_env')
		envHelmVars: dict = EnvRead.as_dict(self.envHelmFilePath)
		for env, var in envHelmVars.items():
			if MEMORY_STRING.K8S.Ki in var:
				pass
			elif MEMORY_STRING.K8S.Mi in var:
				pass
			elif MEMORY_STRING.K8S.Gi in var:
				pass
			else:
				continue
			var = MemoryConverter.convert_k8s_to_docker(var)
			envHelmVars[env] = var

		EnvWrite.from_dict(envHelmVars, self.envHelmFilePath)
		return self

	def copy_templates_to_cwd(self):
		logger.debug(f'{__class__.__name__}.copy_templates_to_cwd_path')
		for yamlTemplate in self.buildYamls:
			templateYaml = os.path.join(self.templatePath, yamlTemplate)
			cwdYaml = os.path.join(self.cwdPath, yamlTemplate)
			copyfile(templateYaml, cwdYaml)

		templateEnvDc = os.path.join(self.templatePath, self.ENV_DOCKER_COMPOSE_FILE)
		copyfile(templateEnvDc, self.envDockerComposeFilePath)

		return self

	def expandvars_in_templates(self):
		logger.debug(f'{__class__.__name__}.expandvars_in_templates')
		for yamlTemplate in self.buildYamls:
			cwdYaml = os.path.join(self.cwdPath, yamlTemplate)
			FileExpandvarsWrite.by_envfile_to_file(self.envFilePath, cwdYaml, cwdYaml)
		return self

	def merge_env_files_in_cwd(self):
		envVars: dict = {}
		envVars.update(EnvRead.as_dict(self.envHelmFilePath))
		envVars.update(EnvRead.as_dict(self.envDockerComposeFilePath))
		EnvWrite(self.envFilePath, Env.dict_to_env_lines(envVars))
		return self

	def put_docker_compose_version(self):
		logger.debug(f'{__class__.__name__}.put_docker_compose_version')
		for yamlTemplate in self.buildYamls:
			cwdYaml = os.path.join(self.cwdPath, yamlTemplate)
			cwdYamlText: str = FileRead.text(cwdYaml).replace(self.DOCKER_COMPOSE_VERSION, self.dockerComposeVersion)
			FileWrite(cwdYaml, cwdYamlText)
		return self

	@staticmethod
	def main(DO_RELOAD, **configurationKwargs):
		logger.debug(f'{__class__.__name__}.main')

		helmConfig: HelmConfigurator = HelmConfigurator.main(DO_RELOAD, **configurationKwargs)

		dockerCompose = DockerComposeConfigurator(**configurationKwargs)
		if DO_RELOAD:
			if dockerCompose.is_reloaded():
				return dockerCompose

			dockerCompose.copy_helm_values_as_env_helm(helmConfig.chartValuesYaml)
			dockerCompose.fix_memory_format_in_env_helm()
			dockerCompose.merge_env_files_in_cwd()
			dockerCompose.copy_templates_to_cwd()
			dockerCompose.expandvars_in_templates()
			dockerCompose.put_docker_compose_version()

		return dockerCompose


class DockerComposeExecutor(ExecutorAbstract, DockerComposeConfigurator):

	def __call__(self, subcommand=None) -> Executor:
		logger.debug(f'{__class__.__name__}.__call__')

		return Executor(DockerKeys.DOCKER_COMPOSE) \
			.with_cwd(self.cwdPath) \
			.with_kwarg(DockerKeys.PROJECT_NAME, self.PROJECT_NAME) \
			.with_subcommand(subcommand)

	def run(self, *argv):
		self().with_args(*argv).spawn()

	def build(self, *argv):
		self(DockerKeys.BUILD).with_args(*argv).with_flags(DockerKeys.PARALLEL).spawn()

	def up(self, *argv):
		self(DockerKeys.UP).with_args(*argv).with_flags(DockerKeys.BUILD).spawn()

	def up_detach(self, *argv):
		self(DockerKeys.UP).with_args(*argv).with_flags(DockerKeys.DETACH, DockerKeys.BUILD).spawn()

	def down(self, *argv):
		self(DockerKeys.DOWN).with_args(*argv).with_flags(DockerKeys.REMOVE_ORPHANS, DockerKeys.VOLUMES).spawn()

	def kill(self):
		self(DockerKeys.KILL).spawn()

	def pull(self, *argv):
		self(DockerKeys.PULL).with_args(*argv).with_flags(DockerKeys.PARALLEL).spawn(exitOnError=False, )

	def push(self, *argv):
		self(DockerKeys.PUSH).with_args(*argv).spawn()

	def logs(self, *argv):
		self(DockerKeys.LOGS).with_flags(DockerKeys.TIMESTAMPS).with_args(*argv).spawn()

	def logs_follow(self, *argv):
		self(DockerKeys.LOGS).with_flags(DockerKeys.FOLLOW, DockerKeys.TIMESTAMPS).with_args(*argv).spawn()
