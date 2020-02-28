#!/usr/bin/env python3.7.7
import os
from shutil import copyfile

from handlers.bin.helm import HelmConfigurator
from handlers.lib.Executor import Executor, ExecutorAbstract
from handlers.lib.FilesHandlers import YamlWrite, EnvRead, EnvWrite, FileExpandvarsWrite, Env, FileRead, FileWrite
from handlers.lib.MemoryConverter import MEMORY_STRING, MemoryConverter
from handlers.lib.Taskset import TasksetConfig
from handlers.lib.common import *

logger = logging.getLogger(__name__)

logger.info("Hello logging!")


class DockerComposeConfigurator(TasksetConfig):
    DOCKER: str = 'docker'
    DOCKER_COMPOSE: str = 'docker-compose'
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
        logger.info(f'{__class__.__name__}.__init__')
        super().__init__(RUNTIME_TYPE=self.DOCKER_COMPOSE, **configurationVariables)

        self.taskPath = os.path.join(self.PATH_TASKSET, self.DOCKER)
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
        logger.info(f'{__class__.__name__}.copy_helm_values_as_env')
        YamlWrite.as_env(yamlPath, self.envHelmFilePath)

    def fix_memory_format_in_env_helm(self):
        logger.info(f'{__class__.__name__}.fix_memory_format_in_env')
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
        logger.info(f'{__class__.__name__}.copy_templates_to_cwd_path')
        for yamlTemplate in self.buildYamls:
            templateYaml = os.path.join(self.templatePath, yamlTemplate)
            cwdYaml = os.path.join(self.cwdPath, yamlTemplate)
            copyfile(templateYaml, cwdYaml)

        templateEnvDc = os.path.join(self.templatePath, self.ENV_DOCKER_COMPOSE_FILE)
        copyfile(templateEnvDc, self.envDockerComposeFilePath)

        return self

    def expandvars_in_templates(self):
        logger.info(f'{__class__.__name__}.expandvars_in_templates')
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
        logger.info(f'{__class__.__name__}.put_docker_compose_version')
        for yamlTemplate in self.buildYamls:
            cwdYaml = os.path.join(self.cwdPath, yamlTemplate)
            cwdYamlText: str = FileRead.text(cwdYaml).replace(self.DOCKER_COMPOSE_VERSION, self.dockerComposeVersion)
            FileWrite(cwdYaml, cwdYamlText)
        return self

    @staticmethod
    def main(DO_RELOAD, **configurationKwargs):
        logger.info(f'{__class__.__name__}.main')

        helmConfig = HelmConfigurator.main(DO_RELOAD, **configurationKwargs)

        dockerCompose = DockerComposeConfigurator(**configurationKwargs)
        if DO_RELOAD:
            if dockerCompose.is_reloaded():
                return dockerCompose

            dockerCompose.copy_helm_values_as_env_helm(helmConfig.projectValuesYaml)
            dockerCompose.fix_memory_format_in_env_helm()
            dockerCompose.merge_env_files_in_cwd()
            dockerCompose.copy_templates_to_cwd()
            dockerCompose.expandvars_in_templates()
            dockerCompose.put_docker_compose_version()

        return dockerCompose


class DockerComposeExecutor(ExecutorAbstract, DockerComposeConfigurator):
    BUILD: str = 'build'
    UP: str = 'up'
    DOWN: str = 'down'
    KILL: str = 'kill'
    PULL: str = 'pull'
    LOGS: str = 'logs'

    KEY_PARALLEL: str = 'parallel'
    KEY_VOLUMES: str = 'volumes'
    KEY_REMOVE_ORPHANS: str = 'remove-orphans'
    KEY_FORCE_RECREATE: str = 'force-recreate'
    KEY_DETACH: str = 'detach'
    KEY_BUILD: str = 'build'
    KEY_ABORT_ON_CONTAINER_EXIT: str = 'abort-on-container-exit'
    KEY_RENEW_ANON_VOLUMES: str = 'renew-anon-volumes'
    KEY_PROJECT_DIRECTORY: str = 'project-directory'
    KEY_PROJECT_NAME: str = 'project-name'
    KEY_TIMESTAMPS: str = 'timestamps'
    KEY_FOLLOW: str = 'follow'

    def __call__(self, subcommand=None) -> Executor:
        logger.info(f'{__class__.__name__}.__call__')

        return Executor(self.DOCKER_COMPOSE) \
            .with_cwd(self.cwdPath) \
            .with_kwarg(self.KEY_PROJECT_NAME, self.PROJECT_NAME) \
            .with_subcommand(subcommand)

    def run(self, *argv):
        return self().with_args(*argv).spawn()

    def build(self, *argv):
        return self(self.BUILD).with_args(*argv).with_flags(self.KEY_PARALLEL).spawn()

    def up(self, *argv):
        return self(self.UP).with_args(*argv).with_flags().spawn()

    def down(self, *argv):
        return self(self.DOWN).with_args(*argv).with_flags(self.KEY_REMOVE_ORPHANS, self.KEY_VOLUMES).spawn()

    def kill(self ):
        return self(self.KILL).spawn()

    def pull(self, *argv):
        return self(self.PULL).with_args(*argv).with_flags(self.KEY_PARALLEL).spawn()

    def logs(self, *argv):
        return self(self.LOGS).with_args(*argv).with_flags(self.KEY_TIMESTAMPS).spawn()


class DockerCompose(DockerComposeConfigurator):

    @staticmethod
    def run(*runArgs, **configurationKwargs):
        logger.info(f'{__class__.__name__}.run')
        return DockerComposeExecutor(**configurationKwargs).run(*runArgs)

    @staticmethod
    def build(*runArgs, **configurationKwargs):
        logger.info(f'{__class__.__name__}.build')
        return DockerComposeExecutor(**configurationKwargs).build(*runArgs)

    @staticmethod
    def up(*runArgs, **configurationKwargs):
        logger.info(f'{__class__.__name__}.up')
        return DockerComposeExecutor(**configurationKwargs).up(*runArgs)

    @staticmethod
    def down(*runArgs, **configurationKwargs):
        logger.info(f'{__class__.__name__}.down')
        return DockerComposeExecutor(DO_RELOAD_HELM=False, **configurationKwargs).down(*runArgs)

    @staticmethod
    def kill(**configurationKwargs):
        logger.info(f'{__class__.__name__}.kill')
        return DockerComposeExecutor(DO_RELOAD_HELM=False, **configurationKwargs).kill()

    @staticmethod
    def pull(*runArgs, **configurationKwargs):
        logger.info(f'{__class__.__name__}.pull')
        return DockerComposeExecutor(**configurationKwargs).pull(*runArgs)

    @staticmethod
    def logs(*runArgs, **configurationKwargs):
        logger.info(f'{__class__.__name__}.logs')
        return DockerComposeExecutor(DO_RELOAD_HELM=False, **configurationKwargs).logs(*runArgs)

    @staticmethod
    def install(*_, **configurationKwargs):
        logger.info(f'{__class__.__name__}.install')

        flagDetach = '--' + DockerComposeExecutor.KEY_DETACH
        flagFollow = '--' + DockerComposeExecutor.KEY_FOLLOW

        yield DockerCompose.down(**configurationKwargs)
        yield DockerCompose.pull(DO_RELOAD_HELM=True, **configurationKwargs)
        yield DockerCompose.build(DO_RELOAD_HELM=False, **configurationKwargs)
        yield DockerCompose.up(flagDetach, DO_RELOAD_HELM=False, **configurationKwargs)
        yield DockerCompose.logs(flagFollow, DO_RELOAD_HELM=False, **configurationKwargs)
