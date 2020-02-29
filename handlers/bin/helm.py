#!/usr/bin/env python3.7.7
import os
from shutil import copyfile

from handlers.lib.Executor import Executor, ExecutorAbstract
from handlers.lib.FilesHandlers import FileExpandvarsWrite, YamlRewrite, FileWrite, YamlConcatWrite
from handlers.lib.Taskset import TasksetConfig
from handlers.lib.common import *

logger = logging.getLogger(__name__)

logger.info("Hello logging!")


class HelmConfigurator(TasksetConfig):
    HELM: str = 'helm'

    CHART: str = 'chart'
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

    logger = logging.getLogger(__name__)

    def __init__(self, **configurationVariables):
        super().__init__(RUNTIME_TYPE=self.HELM, **configurationVariables)
        logger.debug(f'{__class__.__name__}.__init__')

        self.taskPath = os.path.join(self.PATH_TASKSET, self.HELM)
        self.dataPath = os.path.join(self.taskPath, self.DATA)
        self.tempPath = os.path.join(self.taskPath, self.TEMPORARY)
        self.chartPath = os.path.join(self.taskPath, self.CHART)
        self.tempOutputPath = os.path.join(self.tempPath, self.OUTPUT)
        self.chartValuesYaml = os.path.join(self.chartPath, self.VALUES_YAML)

        self.cwdPath = self.taskPath

        os.makedirs(self.taskPath, exist_ok=True)
        os.makedirs(self.dataPath, exist_ok=True)
        os.makedirs(self.tempPath, exist_ok=True)
        os.makedirs(self.tempOutputPath, exist_ok=True)
        os.makedirs(self.chartPath, exist_ok=True)

    def parse_values(self):
        logger.debug(f'{__class__.__name__}.parse_values')
        dataValuesPath = os.path.join(self.dataPath, self.VALUES)
        dataValuesStaticYaml = os.path.join(dataValuesPath, self.STATIC_YAML)
        dataValuesDynamicYaml = os.path.join(dataValuesPath, self.DYNAMIC_YAML)
        tempValuesStaticYaml = os.path.join(self.tempPath, self.VALUES_STATIC_YAML)
        tempValuesDynamicYaml = os.path.join(self.tempPath, self.VALUES_DYNAMIC_YAML)
        tempValuesYaml = os.path.join(self.tempPath, self.VALUES_YAML)

        FileExpandvarsWrite.by_keywords_to_file(dataValuesDynamicYaml, tempValuesDynamicYaml, **self.tasksetConfigMap)
        FileExpandvarsWrite.by_envdir_to_file(self.DIR_ENVFILES, tempValuesDynamicYaml, tempValuesDynamicYaml)
        FileExpandvarsWrite.by_envfile_to_file(dataValuesStaticYaml, dataValuesStaticYaml, tempValuesStaticYaml)
        YamlConcatWrite(tempValuesYaml, tempValuesStaticYaml, tempValuesDynamicYaml)
        FileExpandvarsWrite.by_envfile_to_file(tempValuesYaml, tempValuesYaml, tempValuesYaml)
        YamlRewrite(tempValuesYaml)

        copyfile(tempValuesYaml, self.chartValuesYaml)

    def parse_secrets(self):
        logger.debug(f'{__class__.__name__}.parse_secrets')
        dataSecretsPath = os.path.join(self.dataPath, self.SECRETS)
        dataSecretsDynamicYaml = os.path.join(dataSecretsPath, self.DYNAMIC_YAML)
        tempSecretsYaml = os.path.join(self.tempPath, self.SECRETS_YAML)
        tempSecretsDynamicYaml = os.path.join(self.tempPath, self.SECRETS_DYNAMIC_YAML)
        chartSecretsPath = os.path.join(self.chartPath, self.SECRETS)
        chartSecretsYaml = os.path.join(chartSecretsPath, self.SECRETS_YAML)

        FileExpandvarsWrite.by_envdir_to_file(self.DIR_SECRETFILES, dataSecretsDynamicYaml, tempSecretsDynamicYaml)
        YamlRewrite.flat(tempSecretsDynamicYaml, tempSecretsDynamicYaml)
        YamlConcatWrite.as_is(tempSecretsYaml, tempSecretsDynamicYaml, )

        copyfile(tempSecretsYaml, chartSecretsYaml)

    def parse_chart(self):
        logger.debug(f'{__class__.__name__}.parse_chart')
        tempChartYaml = os.path.join(self.tempPath, self.CHART_YAML)
        dataChartYaml = os.path.join(self.dataPath, self.CHART_YAML)
        chartChartYaml = os.path.join(self.chartPath, self.CHART_YAML)
        FileExpandvarsWrite.by_keywords_to_file(dataChartYaml, tempChartYaml, CHART_VERSION=self.PROJECT_VERSION)
        copyfile(tempChartYaml, chartChartYaml)

    @staticmethod
    def main(DO_RELOAD, DO_SORT_CONFIG_YAMLS=True, **configurationKwargs):
        logger.debug(f'{__class__.__name__}.main')

        helm: HelmConfigurator = HelmConfigurator(**configurationKwargs)

        if DO_RELOAD:
            if helm.is_reloaded():
                return helm

            if DO_SORT_CONFIG_YAMLS:
                YamlRewrite.multiple_from_dir(helm.dataPath)

            helm.parse_values()
            helm.parse_secrets()
            helm.parse_chart()

        return helm


class HelmExecutor(ExecutorAbstract, HelmConfigurator):
    INSTALL: str = 'install'
    UNINSTALL: str = 'uninstall'
    LINT: str = 'lint'
    TEMPLATE: str = 'template'
    DRY_RUN: str = 'dry-run'
    REPLACE: str = 'replace'
    DEBUG: str = 'debug'
    UPGRADE: str = 'upgrade'
    FORCE: str = 'force'
    logger = logging.getLogger(__name__)

    def __call__(self, subcommand: str = None) -> Executor:
        logger.debug(f'{__class__.__name__}.__call__')
        return Executor(self.HELM).with_args(subcommand).with_cwd(self.cwdPath)

    def run(self, *argv):
        logger.debug(f'{__class__.__name__}.run')
        self().with_args(*argv).spawn()

    def install(self, doUntilOk=False):
        logger.debug(f'{__class__.__name__}.install')
        self(self.INSTALL).with_args(self.PROJECT_NAME, self.CHART).with_flags(self.REPLACE, self.DEBUG).exec(doUntilOk=doUntilOk)

    def uninstall(self):
        logger.debug(f'{__class__.__name__}.uninstall')
        self(self.UNINSTALL).with_args(self.PROJECT_NAME).with_flags(self.DEBUG).exec(exitOnError=False)

    def upgrade(self):
        logger.debug(f'{__class__.__name__}.upgrade')
        self(self.UPGRADE).with_args(self.PROJECT_NAME, self.CHART).with_flags(self.DEBUG, self.FORCE).exec(exitOnError=False)

    def dry_run(self):
        logger.debug(f'{__class__.__name__}.dry_run')

        out: str = self(self.INSTALL) \
            .with_args(self.PROJECT_NAME, self.CHART) \
            .with_flags(self.REPLACE, self.DEBUG, self.DRY_RUN) \
            .exec()

        stdoutPath = os.path.join(self.tempOutputPath, self.DRY_RUN + ".yaml")
        FileWrite(stdoutPath, out)

    def lint(self):
        logger.debug(f'{__class__.__name__}.lint')
        self(self.LINT, ).with_args(self.CHART).exec()

    def template(self):
        logger.debug(f'{__class__.__name__}.template')
        out: str = self(self.TEMPLATE).with_args(self.PROJECT_NAME, self.CHART).exec()
        stdoutPath = os.path.join(self.tempOutputPath, self.TEMPLATE + ".yaml")
        FileWrite(stdoutPath, out)


class Helm(HelmConfigurator):
    logger = logging.getLogger(__name__)

    @staticmethod
    def run(*args, **configurationKwargs):
        logger.info(f'{__class__.__name__}.run')
        HelmExecutor(**configurationKwargs).run(*args)

    @staticmethod
    def install(**configurationKwargs):
        logger.info(f'{__class__.__name__}.install')
        HelmExecutor(**configurationKwargs).install()

    @staticmethod
    def uninstall(**configurationKwargs):
        logger.info(f'{__class__.__name__}.uninstall')
        try:
            HelmExecutor(**configurationKwargs).uninstall()
        except Exception as err:
            logger.exception(f'{__class__.__name__}.uninstall FAILED due to {err}')
            pass

    @staticmethod
    def upgrade(**configurationKwargs):
        logger.info(f'{__class__.__name__}.upgrade')
        HelmExecutor(**configurationKwargs).upgrade()

    @staticmethod
    def reinstall(**configurationKwargs):
        logger.info(f'{__class__.__name__}.reinstall')

        doReload = configurationKwargs['DO_RELOAD']
        configurationKwargs['DO_RELOAD'] = False
        HelmExecutor(**configurationKwargs).uninstall()
        configurationKwargs['DO_RELOAD'] = doReload
        HelmExecutor(**configurationKwargs).install(doUntilOk=True)

    @staticmethod
    def dry_run(**configurationKwargs):
        logger.info(f'{__class__.__name__}.dry_run')
        HelmExecutor(**configurationKwargs).dry_run()

    @staticmethod
    def lint(**configurationKwargs):
        logger.info(f'{__class__.__name__}.lint')
        HelmExecutor(**configurationKwargs).lint()

    @staticmethod
    def template(**configurationKwargs):
        logger.info(f'{__class__.__name__}.template')
        HelmExecutor(**configurationKwargs).template()

    @staticmethod
    def full_check(**configurationKwargs):
        logger.info(f'{__class__.__name__}.full_check')
        Helm.lint(**configurationKwargs),
        Helm.template(**configurationKwargs)
        Helm.dry_run(**configurationKwargs)
