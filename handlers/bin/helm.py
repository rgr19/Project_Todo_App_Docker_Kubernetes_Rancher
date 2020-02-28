#!/usr/bin/env python3.7.7
import os
from shutil import copyfile

from handlers.lib.Executor import Executor, ExecutorOutputParser, ExecutorAbstract
from handlers.lib.FilesHandlers import FileExpandvarsWrite, YamlRewrite, FileWrite, YamlConcatWrite
from handlers.lib.Taskset import TasksetConfig
from handlers.lib.common import *

logger = logging.getLogger(__name__)

logger.info("Hello logging!")


class HelmConfigurator(TasksetConfig):
    HELM: str = 'helm'

    OUTPUT: str = 'output'
    VALUES: str = 'values'
    SECRETS: str = 'secrets'
    STATIC_YAML: str = 'static.yaml'
    DYNAMIC_YAML: str = 'dynamic.yaml'
    CHART_YAML: str = 'Chart.yaml'
    VALUES_YAML: str = 'values.yaml'
    SECRETS_YAML: str = 'secrets.yaml'
    VALUES_STATIC_YAML: str = 'values.static.yaml'
    VALUES_DYNAMIC_YAML: str = 'values.dynamic.yaml'
    SECRETS_DYNAMIC_YAML: str = 'secrets.dynamic.yaml'

    def __init__(self, **configurationVariables):
        super().__init__(RUNTIME_TYPE=self.HELM, **configurationVariables)
        logger.info(f'{__class__.__name__}.__init__')

        self.taskPath = os.path.join(self.PATH_TASKSET, self.HELM)
        self.configPath = os.path.join(self.taskPath, self.TEMPLATE)
        self.tempPath = os.path.join(self.taskPath, self.TEMPORARY)
        self.projectPath = os.path.join(self.taskPath, self.PROJECT_NAME)
        self.tempOutputPath = os.path.join(self.tempPath, self.OUTPUT)
        self.projectValuesYaml = os.path.join(self.projectPath, self.VALUES_YAML)

        self.cwdPath = self.taskPath

        os.makedirs(self.taskPath, exist_ok=True)
        os.makedirs(self.configPath, exist_ok=True)
        os.makedirs(self.tempPath, exist_ok=True)
        os.makedirs(self.tempOutputPath, exist_ok=True)
        os.makedirs(self.projectPath, exist_ok=True)

    def parse_values(self):
        logger.info(f'{__class__.__name__}.parse_values')
        configValuesPath = os.path.join(self.configPath, self.VALUES)
        configValuesStaticYaml = os.path.join(configValuesPath, self.STATIC_YAML)
        configValuesDynamicYaml = os.path.join(configValuesPath, self.DYNAMIC_YAML)
        tempValuesStaticYaml = os.path.join(self.tempPath, self.VALUES_STATIC_YAML)
        tempValuesDynamicYaml = os.path.join(self.tempPath, self.VALUES_DYNAMIC_YAML)
        tempValuesYaml = os.path.join(self.tempPath, self.VALUES_YAML)

        FileExpandvarsWrite.by_envfile_to_file(configValuesStaticYaml, configValuesStaticYaml, tempValuesStaticYaml)
        FileExpandvarsWrite.by_envdir_to_file(self.DIR_ENVFILES, configValuesDynamicYaml, tempValuesDynamicYaml)
        YamlConcatWrite(tempValuesYaml, tempValuesStaticYaml, tempValuesDynamicYaml)
        copyfile(tempValuesYaml, self.projectValuesYaml)

    def parse_secrets(self):
        logger.info(f'{__class__.__name__}.parse_secrets')
        configSecretsPath = os.path.join(self.configPath, self.SECRETS)
        configSecretsDynamicYaml = os.path.join(configSecretsPath, self.DYNAMIC_YAML)
        tempSecretsYaml = os.path.join(self.tempPath, self.SECRETS_YAML)
        tempSecretsDynamicYaml = os.path.join(self.tempPath, self.SECRETS_DYNAMIC_YAML)
        projectSecretsPath = os.path.join(self.projectPath, self.SECRETS)
        projectSecretsYaml = os.path.join(projectSecretsPath, self.SECRETS_YAML)

        FileExpandvarsWrite.by_envdir_to_file(self.DIR_SECRETFILES, configSecretsDynamicYaml, tempSecretsDynamicYaml)
        YamlRewrite.flat(tempSecretsDynamicYaml, tempSecretsDynamicYaml)
        YamlConcatWrite.as_is(tempSecretsYaml, tempSecretsDynamicYaml, )
        copyfile(tempSecretsYaml, projectSecretsYaml)

    def parse_chart(self):
        logger.info(f'{__class__.__name__}.parse_chart')
        tempChartYaml = os.path.join(self.tempPath, self.CHART_YAML)
        configChartYaml = os.path.join(self.configPath, self.CHART_YAML)
        projectChartYaml = os.path.join(self.projectPath, self.CHART_YAML)
        FileExpandvarsWrite.by_keywords_to_file(configChartYaml, tempChartYaml, CHART_VERSION=self.PROJECT_VERSION)
        copyfile(tempChartYaml, projectChartYaml)

    @staticmethod
    def main(DO_RELOAD, DO_SORT_CONFIG_YAMLS=True, **configurationKwargs):
        logger.info(f'{__class__.__name__}.main')

        helm = HelmConfigurator(**configurationKwargs)

        if DO_RELOAD:
            if helm.is_reloaded():
                return helm

            if DO_SORT_CONFIG_YAMLS:
                YamlRewrite.multiple_from_dir(helm.configPath)

            helm.parse_values()
            helm.parse_secrets()
            helm.parse_chart()

        return helm


class HelmExecutor(ExecutorAbstract, HelmConfigurator):
    INSTALL: str = 'install'
    LINT: str = 'lint'
    TEMPLATE: str = 'template'
    DRY_RUN: str = 'dry-run'
    REPLACE: str = 'replace'
    DEBUG: str = 'debug'

    def __call__(self, subcommand: str = None) -> Executor:
        return Executor(self.HELM, subcommand, self.PROJECT_NAME).with_cwd(self.cwdPath)

    def install(self):
        return self(self.INSTALL).with_args(self.PROJECT_NAME).with_flags(self.REPLACE, self.DEBUG).exec()

    def dry_run(self):
        processOutput: ExecutorOutputParser = self(self.INSTALL) \
            .with_args(self.PROJECT_NAME) \
            .with_flags(self.REPLACE, self.DEBUG, self.DRY_RUN) \
            .exec()

        stdoutPath = os.path.join(self.tempOutputPath, self.DRY_RUN + ".stdout.yaml")
        stderrPath = os.path.join(self.tempOutputPath, self.DRY_RUN + ".stderr.log")
        FileWrite(stdoutPath, processOutput.stdout)
        FileWrite(stderrPath, processOutput.stderr)

    def lint(self):
        return self(self.LINT).exec()

    def template(self):
        return self(self.TEMPLATE).exec()


class Helm(HelmConfigurator):

    @staticmethod
    def install(**configurationKwargs):
        logger.info(f'{__class__.__name__}.install')
        return HelmExecutor(**configurationKwargs).install()

    @staticmethod
    def dry_run(**configurationKwargs):
        logger.info(f'{__class__.__name__}.dry_run')
        return HelmExecutor(**configurationKwargs).dry_run()

    @staticmethod
    def lint(**configurationKwargs):
        logger.info(f'{__class__.__name__}.lint')
        configurationKwargs['DO_RELOAD_HELM'] = False
        return HelmExecutor(**configurationKwargs).lint()

    @staticmethod
    def template(**configurationKwargs):
        logger.info(f'{__class__.__name__}.template')
        return HelmExecutor(**configurationKwargs).template()

    @staticmethod
    def full_check(**configurationKwargs):
        logger.info(f'{__class__.__name__}.full_check')
        yield Helm.lint(**configurationKwargs)
        yield Helm.template(**configurationKwargs)
        yield Helm.dry_run(**configurationKwargs)
