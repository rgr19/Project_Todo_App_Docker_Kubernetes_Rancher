#!/usr/bin/env python3.7.7
import json
import os
from shutil import copyfile, copytree, ignore_patterns, rmtree

from handlers.lib.Executor import Executor, ExecutorAbstract
from handlers.lib.FilesHandlers import FileExpandvarsWrite, YamlRewrite, FileWrite, YamlConcatWrite
from handlers.lib.Git import GitExecutor
from handlers.lib.Logger import Logger
from handlers.lib.Taskset import TasksetConfig
from handlers.lib.VersionHandlers import version_parser

logger = Logger.build(__name__)


class HelmConfigurator(TasksetConfig):
	HELM: str = 'helm'

	CHART: str = 'chart'
	CHARTS: str = 'charts'
	REPO: str = 'repo'
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
		logger.info(f'{__class__.__name__}.__init__')
		super().__init__(RUNTIME_TYPE=self.HELM, **configurationVariables)

		self.taskPath = os.path.join(self.PATH_TASKSET, self.HELM)
		self.dataPath = os.path.join(self.taskPath, self.DATA)
		self.tempPath = os.path.join(self.taskPath, self.TEMPORARY)
		self.chartPath = os.path.join(self.taskPath, self.CHART)
		self.repoPath = os.path.join(self.taskPath, self.REPO)
		self.tempOutputPath = os.path.join(self.tempPath, self.OUTPUT)
		self.chartValuesYaml = os.path.join(self.chartPath, self.VALUES_YAML)
		self.repoChartsPath = os.path.join(self.repoPath, self.CHARTS)
		self.cwdPath = self.taskPath

		os.makedirs(self.taskPath, exist_ok=True)
		os.makedirs(self.dataPath, exist_ok=True)
		os.makedirs(self.tempPath, exist_ok=True)
		os.makedirs(self.tempOutputPath, exist_ok=True)
		os.makedirs(self.chartPath, exist_ok=True)

	def parse(self):
		logger.info(f'{__class__.__name__}.parse')
		self.parse_values()
		self.parse_secrets()
		self.parse_chart()

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
		YamlConcatWrite.as_is(tempSecretsYaml, tempSecretsDynamicYaml)

		copyfile(tempSecretsYaml, chartSecretsYaml)

	def parse_chart(self):
		logger.debug(f'{__class__.__name__}.parse_chart')
		tempChartYaml = os.path.join(self.tempPath, self.CHART_YAML)
		dataChartYaml = os.path.join(self.dataPath, self.CHART_YAML)
		chartChartYaml = os.path.join(self.chartPath, self.CHART_YAML)
		FileExpandvarsWrite.by_keywords_to_file(dataChartYaml, tempChartYaml, CHART_VERSION=self.PROJECT_VERSION)
		copyfile(tempChartYaml, chartChartYaml)

	def copy_chart_to_repo(self):
		logger.debug(f'{__class__.__name__}.copy_chart_to_repo')
		repoChartsProjectPath = os.path.join(self.repoChartsPath, self.PROJECT_NAME)
		if os.path.exists(repoChartsProjectPath):
			rmtree(repoChartsProjectPath)
		copytree(self.chartPath, repoChartsProjectPath, ignore=ignore_patterns('secrets'))

	def save_helm_config_to_envfiles(self, **configurationKwargs):
		logger.debug(f'{__class__.__name__}.save_helm_config_to_envfiles')
		helmVersion = HelmExecutor().version()
		FileWrite(self.HELM_VERSION, helmVersion)
		return self

	def save_k8s_config_to_envfiles(self, **configurationKwargs):
		logger.debug(f'{__class__.__name__}.save_k8s_config_to_envfiles')
		kubectlVersion = KubectlExecutor().version_client()
		FileWrite(self.KUBECTL_VERSION, kubectlVersion)
		return self

	@staticmethod
	def main(DO_RELOAD=False, DO_SORT_CONFIG_YAMLS=True, **configurationKwargs):
		logger.info(f'{__class__.__name__}.main')

		helm: HelmConfigurator = HelmConfigurator(**configurationKwargs)

		if DO_RELOAD:
			if helm.is_reloaded():
				return helm

			if DO_SORT_CONFIG_YAMLS:
				YamlRewrite.multiple_from_dir(helm.dataPath)

			helm.parse()

		return helm

	@staticmethod
	def repo(DO_RELOAD=False, DO_SORT_CONFIG_YAMLS=True, **configurationKwargs):

		helm: HelmConfigurator = HelmConfigurator.main(DO_RELOAD, DO_SORT_CONFIG_YAMLS, **configurationKwargs)
		helm.save_helm_config_to_envfiles(**configurationKwargs)
		helm.save_k8s_config_to_envfiles(**configurationKwargs)
		GitExecutor(helm.repoPath).checkout_branch(GitExecutor.MASTER)
		helm.copy_chart_to_repo()

		return helm


class KubectlExecutor(ExecutorAbstract):
	KUBECTL: str = 'kubectl'
	VERSION: str = 'version'
	OUTPUT: str = 'output'
	JSON: str = 'json'

	def __call__(self, subcommand: str = None) -> Executor:
		logger.debug(f'{__class__.__name__}.__call__')
		return Executor(self.KUBECTL).with_args(subcommand)

	def run(self, *argv):
		logger.debug(f'{__class__.__name__}.run')
		self().with_args(*argv).spawn()

	def version(self):
		logger.debug(f'{__class__.__name__}.version')
		version = self(self.VERSION).with_kwarg(self.OUTPUT, self.JSON).exec()
		return json.loads(version)

	def version_client(self):
		logger.debug(f'{__class__.__name__}.version_client')
		version = self.version()['clientVersion']
		version = '.'.join((version['major'], version['minor'], '0'))
		return version_parser(version)

	def version_server(self):
		logger.debug(f'{__class__.__name__}.version_server')
		version = self.version()['serverVersion']
		version = '.'.join((version['major'], version['minor'], '0'))
		return version_parser(version)


class HelmExecutor(ExecutorAbstract, HelmConfigurator):
	INSTALL: str = 'install'
	UNINSTALL: str = 'uninstall'
	LINT: str = 'lint'
	TEMPLATE: str = 'template'
	DRY_RUN: str = 'dry-run'
	REPLACE: str = 'replace'
	DEBUG: str = 'debug'
	UPGRADE: str = 'upgrade'
	VERSION: str = 'version'
	SHORT: str = 'short'
	FORCE: str = 'force'

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

	def dry_run(self, quiet=False):
		logger.debug(f'{__class__.__name__}.dry_run')

		out: str = self(self.INSTALL) \
			.with_args(self.PROJECT_NAME, self.CHART) \
			.with_flags(self.REPLACE, self.DEBUG, self.DRY_RUN) \
			.exec(quiet=quiet)

		stdoutPath = os.path.join(self.tempOutputPath, self.DRY_RUN + ".yaml")
		FileWrite(stdoutPath, out)

	def lint(self):
		logger.debug(f'{__class__.__name__}.lint')
		self(self.LINT).with_args(self.CHART).exec()

	def lint_repo(self):
		logger.debug(f'{__class__.__name__}.lint_repo_chart')
		self(self.LINT).with_args(self.PROJECT_NAME).with_cwd(self.repoChartsPath).exec()

	def template(self):
		logger.debug(f'{__class__.__name__}.template')
		out: str = self(self.TEMPLATE).with_args(self.PROJECT_NAME, self.CHART).exec()
		stdoutPath = os.path.join(self.tempOutputPath, self.TEMPLATE + ".yaml")
		FileWrite(stdoutPath, out)

	def version(self):
		logger.debug(f'{__class__.__name__}.version')
		return version_parser(self(self.VERSION).with_flags(self.SHORT).exec(exitOnError=False))
