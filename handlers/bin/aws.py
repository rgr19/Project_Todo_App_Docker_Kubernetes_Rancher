#!/usr/bin/env python3.7
import os
from shutil import copyfile

from handlers.bin.helm import HelmConfigurator
from handlers.lib.Executor import ExecutorAbstract, Executor
from handlers.lib.FilesHandlers import YamlWrite, EnvRead, EnvWrite, Env, FileExpandvarsWrite
from handlers.lib.MemoryConverter import MEMORY_STRING, MemoryConverter
from handlers.lib.Taskset import TasksetConfig
from handlers.lib.common import *

logger = logging.getLogger(__name__)

logger.info("Hello logging!")


class AwsConfigurator(TasksetConfig):
    AWS: str = 'aws'
    DATA: str = 'template'
    TEMP_DIR: str = 'temporary'
    ENV_FILE: str = '.env'
    ENV_AWS_FILE: str = ENV_FILE + '.aws'
    DOCKERRUN_AWS_JSON_FILE: str = 'Dockerrun.aws.json'

    def __init__(self, **configurationVariables):
        logger.info(f'{__class__.__name__}.__init__')
        super().__init__(RUNTIME_TYPE=self.AWS, **configurationVariables)

        self.taskPath = os.path.join(self.PATH_TASKSET, self.AWS)
        self.templatePath = os.path.join(self.taskPath, self.TEMPLATE)

        self.tempPath = os.path.join(self.taskPath, self.TEMP_DIR)
        self.envFilePath = os.path.join(self.taskPath, self.ENV_FILE)
        self.envHelmFilePath = os.path.join(self.taskPath, self.ENV_FILE)
        self.envAwsFilePath = os.path.join(self.taskPath, self.ENV_AWS_FILE)
        self.dockerRunAwsJsonPath = os.path.join(self.taskPath, self.DOCKERRUN_AWS_JSON_FILE)

        self.cwdPath = self.taskPath

    def copy_helm_values_as_env_helm(self, projectValuesYaml):
        logger.info(f'{__class__.__name__}.copy_helm_values_as_env')
        YamlWrite.as_env(projectValuesYaml, self.envHelmFilePath)

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
            var = MemoryConverter.convert_k8s_to_aws(var)
            envHelmVars[env] = var

        EnvWrite.from_dict(envHelmVars, self.envHelmFilePath)
        return self

    def copy_aws_templates_to_cwd(self):
        logger.info(f'{__class__.__name__}.copy_aws_templates_to_cwd')

        envAwsTemplatePath = os.path.join(self.templatePath, self.ENV_AWS_FILE)
        copyfile(envAwsTemplatePath, self.envAwsFilePath)

        dockerRunAwsJsonTemplatePath = os.path.join(self.templatePath, self.DOCKERRUN_AWS_JSON_FILE)
        copyfile(dockerRunAwsJsonTemplatePath, self.dockerRunAwsJsonPath)

    def merge_env_files_in_cwd(self):
        logger.info(f'{__class__.__name__}.merge_env_files_in_cwd')
        envVars: dict = {}
        envVars.update(EnvRead.as_dict(self.envHelmFilePath))
        envVars.update(EnvRead.as_dict(self.envAwsFilePath))
        EnvWrite(self.envFilePath, Env.dict_to_env_lines(envVars))
        return self

    def expandvars_at_templates_in_cwd(self):
        logger.info(f'{__class__.__name__}.expandvars_in_templates')
        FileExpandvarsWrite.by_envfile_to_file(self.envFilePath, self.dockerRunAwsJsonPath, self.dockerRunAwsJsonPath)
        return self

    @staticmethod
    def select_elastic_beanstalk_application_env(AWS_APP_ENV=None, **configurationKwargs):
        logger.info(f'{__class__.__name__}.')
        Aws.use(AWS_APP_ENV, **configurationKwargs)

    @staticmethod
    def main(AWS_APP_ENV=None, DO_RELOAD=False, **configurationKwargs):
        logger.info(f'{__class__.__name__}.main')

        helmConfig: HelmConfigurator = HelmConfigurator.main(DO_RELOAD, **configurationKwargs)

        awsConfig = AwsConfigurator(**configurationKwargs)
        if DO_RELOAD:
            if awsConfig.is_reloaded():
                return awsConfig

            awsConfig.copy_helm_values_as_env_helm(helmConfig.chartValuesYaml)
            awsConfig.fix_memory_format_in_env_helm()
            awsConfig.copy_aws_templates_to_cwd()
            awsConfig.merge_env_files_in_cwd()
            awsConfig.expandvars_at_templates_in_cwd()
            awsConfig.select_elastic_beanstalk_application_env(AWS_APP_ENV, **configurationKwargs)

        return awsConfig


class AwsExecutor(ExecutorAbstract, AwsConfigurator):
    UPLOAD_ENV: str = 'UPLOAD_ENV'
    ELASTIC_BEANSTALK: str = 'eb'
    USE: str = 'use'
    SETENV: str = 'setenv'

    def __call__(self, subcommand=None):
        command = [self.ELASTIC_BEANSTALK]

        return Executor(command) \
            .with_cwd(self.cwdPath) \
            .with_subcommand(subcommand)

    def run(self, *argv):
        logger.info(f'{__class__.__name__}.run')
        return self.__call__().with_args(*argv).spawn()

    def setenv(self, *argv, **envVars):
        logger.info(f'{__class__.__name__}.setenv')
        return self.__call__(self.SETENV).with_envvars(**envVars).with_args(*argv).spawn()

    def list(self, *argv):
        logger.info(f'{__class__.__name__}.list')
        return self.__call__(self.USE).with_args(*argv).exec()

    def use(self, awsEnv=None, *argv):
        logger.info(f'{__class__.__name__}.use')
        if not awsEnv:
            logger.warning(f'{__class__.__name__}.use => No AWS App Environment provided. Trying to find.')
            awsEnvList: list = self.list()
            if awsEnvList:
                awsEnv = awsEnvList
        if awsEnv:
            return self.__call__(self.USE).with_args(awsEnv, *argv).spawn()
        else:
            logger.warning(f'{__class__.__name__}.use => No AWS App Environment provided/exists.')


class Aws(AwsConfigurator):

    @staticmethod
    def run(*runArgs, **configurationKwargs):
        logger.info(f'{__class__.__name__}.run')
        return AwsExecutor(**configurationKwargs).run(*runArgs)

    @staticmethod
    def setenv(*runArgs, **configurationKwargs):
        logger.info(f'{__class__.__name__}.setenv')
        return AwsExecutor(**configurationKwargs).run(*runArgs)

    @staticmethod
    def use(*runArgs, **configurationKwargs):
        logger.info(f'{__class__.__name__}.setenv')
        return AwsExecutor(**configurationKwargs).use(*runArgs)

    @staticmethod
    def list(*runArgs, **configurationKwargs):
        logger.info(f'{__class__.__name__}.setenv')
        return AwsExecutor(**configurationKwargs).list(*runArgs)
