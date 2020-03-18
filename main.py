#!/usr/bin/env python3.7
import argparse
import os
import sys
from pprint import pprint
from types import GeneratorType

from handlers.bin.aws import Aws
from handlers.bin.docker_compose import DockerCompose
from handlers.bin.helm import Helm
from handlers.bin.travis import Travis, TravisSubmodule
from handlers.lib.Logger import Logger
from handlers.lib.VersionHandlers import parse_project_version, parse_images_version, LAST


class SetupParserTasks(object):

	def __init__(self, parser):
		# construct the argument parser and parse the arguments
		self.mainParser = parser

		self.operationParsers = self.mainParser.add_subparsers(dest='OPERATION', required=True, description="Todo App operations selector.")
		self.setup_helm_parser()
		self.setup_docker_compose_parser()
		self.setup_travis_parser()
		self.setup_aws_parser()
		# self.setup_kompose_parser()
		# self.setup_k8s_parser()
		self.setup_automate()
		self.setup_ci()

	def setup_docker_compose_parser(self):
		epilog = 'Note: Helm values.yaml will be converted to .env.helm and used.'
		dockerCompose = self.operationParsers.add_parser("DOCKER_COMPOSE", aliases=['DC'], epilog=epilog)
		dockerCompose.set_defaults(config_task=DockerCompose.main, DO_RELOAD=False)

		tasks = dockerCompose.add_subparsers(dest='TASK', required=True, )

		task = tasks.add_parser("BUILD", aliases=['B', 'build'], )
		task.set_defaults(main_task=DockerCompose.build, DO_RELOAD=True)
		task = tasks.add_parser("UP", aliases=['U', 'up'], )
		task.set_defaults(main_task=DockerCompose.up, DO_RELOAD=True)
		task = tasks.add_parser("DOWN", aliases=['D', 'down'], )
		task.set_defaults(main_task=DockerCompose.down)
		task = tasks.add_parser("KILL", aliases=['K', 'kill'], )
		task.set_defaults(main_task=DockerCompose.kill)
		task = tasks.add_parser("PULL", aliases=['PL', 'pull'], )
		task.set_defaults(main_task=DockerCompose.pull, DO_RELOAD=True)
		task = tasks.add_parser("PUSH", aliases=['PS', 'push'], )
		task.set_defaults(main_task=DockerCompose.push, DO_RELOAD=True)
		task = tasks.add_parser("LOGS", aliases=['L', 'logs'], )
		task.set_defaults(main_task=DockerCompose.logs)
		task = tasks.add_parser("INSTALL", aliases=['I', 'install'], )
		task.set_defaults(main_task=DockerCompose.install, DO_RELOAD=True)

	def setup_helm_parser(self, ):
		helm = self.operationParsers.add_parser("HELM", aliases=['H'], )
		helm.add_argument("-s", "--sort-config-yamls", dest='DO_SORT_CONFIG_YAMLS', type=bool, required=False, default=True)
		helm.set_defaults(config_task=Helm.main, DO_RELOAD=True)

		tasks = helm.add_subparsers(dest='TASK', required=True, )
		task = tasks.add_parser("RUN", aliases=['R', 'run'], )
		task.set_defaults(main_task=Helm.run)
		task = tasks.add_parser("LINT", aliases=['L', 'lint'], )
		task.set_defaults(main_task=Helm.lint)
		task = tasks.add_parser("TEMPLATE", aliases=['T', 'template'])
		task.set_defaults(main_task=Helm.template)
		task = tasks.add_parser("DRY-RUN", aliases=['D', 'dry-run'])
		task.set_defaults(main_task=Helm.dry_run)
		task = tasks.add_parser("FULL_CHECK", aliases=['F', 'full-check'])
		task.set_defaults(main_task=Helm.full_check)
		task = tasks.add_parser("INSTALL", aliases=['I', 'install'])
		task.set_defaults(main_task=Helm.install)
		task = tasks.add_parser("UNINSTALL", aliases=['U', 'uninstall'])
		task.set_defaults(main_task=Helm.uninstall)
		task = tasks.add_parser("UPGRADE", aliases=['u', 'upgrade'])
		task.set_defaults(main_task=Helm.upgrade)
		task = tasks.add_parser("COPY_TO_REPO", aliases=['copy', 'copy-to-repo'])
		task.set_defaults(main_task=Helm.copy_chart_to_repo)

	def setup_aws_parser(self):
		aws = self.operationParsers.add_parser("AWS", aliases=['A'], )
		aws.add_argument("-a", "--aws_task-app-env", dest='AWS_APP_ENV', type=str, required=False)
		aws.set_defaults(config_task=Aws.main)

		tasks = aws.add_subparsers(dest='TASK', required=True, )

		task = tasks.add_parser("RUN", aliases=['R', 'run'], )
		task.set_defaults(main_task=Aws.run)
		task = tasks.add_parser("SETENV", aliases=['S', 'setenv'], )
		task.set_defaults(main_task=Aws.setenv)
		task = tasks.add_parser("USE", aliases=['U', 'use'], )
		task.set_defaults(main_task=Aws.use)
		task = tasks.add_parser("LIST", aliases=['L', 'list'], )
		task.set_defaults(main_task=Aws.list)

	def setup_travis_parser(self):
		travis = self.operationParsers.add_parser("TRAVIS", aliases=['T'], )
		travis.add_argument("-m", "--git-message", dest='gitMessage', type=str, required=False)
		travis.set_defaults(config_task=Travis.main, DO_RELOAD=True)

		tasks = travis.add_subparsers(dest='TASK', required=True, )

		task = tasks.add_parser("LOGS", aliases=['L'], )
		task.set_defaults(main_task=Travis.logs)
		task = tasks.add_parser("BASIC", aliases=['B'], )
		task.set_defaults(main_task=Travis.basic)
		task = tasks.add_parser("AWS", aliases=['A'], )
		task.set_defaults(main_task=Travis.aws)
		task = tasks.add_parser("HELM_REPO", aliases=['HR'], )
		task.set_defaults(main_task=TravisSubmodule.helm)

	def setup_kompose_parser(self):
		argsKompose = self.operationParsers.add_parser("KOMPOSE", aliases=['k'], )

	def setup_k8s_parser(self):
		argsK8s = self.operationParsers.add_parser("K8S", aliases=['K'], )

	def setup_automate(self, ):
		automate = self.operationParsers.add_parser("AUTOMATE", aliases=['a'], )
		automate.set_defaults(config_task=[DockerCompose.main, Travis.main, Helm.main])
		automate.set_defaults(main_task=[DockerCompose.build, Travis.basic, Helm.reinstall])
		automate.set_defaults(DO_RELOAD=True)
		
	def setup_ci(self):
		automate = self.operationParsers.add_parser("CI", aliases=['ci'], )
		automate.set_defaults(config_task=[DockerCompose.main, Travis.main, Helm.main])
		automate.set_defaults(main_task=[DockerCompose.build, Travis.basic, Travis.logs, TravisSubmodule.helm, Travis.logs])
		automate.set_defaults(DO_RELOAD=True)
		
	def parse_args(self, argv, ):
		return self.mainParser.parse_args(argv, )


def main(parser, argv):
	logger.info(f' main : {argv}')
	SetupParserTasks(parser)

	parsedArgs, customArgs = parser.parse_known_args(argv)
	kwargsDict = vars(parsedArgs)

	logger.info(f' PARSED ARGS: ')
	pprint(kwargsDict)
	logger.info(f' CUSTOM ARGS: ')
	pprint(customArgs)

	config_task = kwargsDict.pop('config_task')
	main_task = kwargsDict.pop('main_task')

	os.environ['DRY_RUN'] = 'True' if kwargsDict.pop('DRY_RUN') else ''

	kwargsDict['PROJECT_VERSION'] = parse_project_version(kwargsDict.pop('PROJECT_VERSION'))
	kwargsDict['IMAGES_VERSION'] = parse_images_version(kwargsDict.pop('IMAGES_VERSION'))

	if isinstance(config_task, list):
		for next_config_task in config_task:
			next_config_task(**kwargsDict)
	elif callable(config_task):
		config_task(**kwargsDict)

	if isinstance(main_task, (tuple, list)):
		for next_main_task in main_task:
			out = next_main_task(*customArgs, **kwargsDict)
			if isinstance(out, GeneratorType):
				while next(out):
					pass
	elif callable(main_task):
		out = main_task(*customArgs, **kwargsDict)
		if isinstance(out, GeneratorType):
			while next(out):
				pass
		elif isinstance(out, (tuple, list)):
			while next(out):
				pass


if __name__ == '__main__':
	logger = Logger.set_level('DEBUG').build(__name__)

	mainParser = argparse.ArgumentParser(prog="MAIN", description="Project Main CLI.")
	mainParser.add_argument('-d', '--dry-run', dest='DRY_RUN', default=False, required=False, action='store_true')
	mainParser.add_argument('-b', '--build-type', dest='BUILD_TYPE', default='prod', required=False, choices='DEV PROD'.split())
	mainParser.add_argument('-p', '--project-name', dest='PROJECT_NAME', default='todo-app', required=False)
	mainParser.add_argument('-e', '--envfiles-dir', dest='DIR_ENVFILES', default='.envfiles', required=False)
	mainParser.add_argument('-s', '--secretfiles-dir', dest='DIR_SECRETFILES', default='.secretfiles', required=False)

	mainParser.add_argument("-v", "--project-version", dest='PROJECT_VERSION', default=LAST, required=False, type=str,
	                        help="Set project version in the form `x[.x[.x]]`. Given `NEXT/PREV/LAST` compute version based on cache in .chart_versions_used.")
	mainParser.add_argument("-V", "--images-version", dest='IMAGES_VERSION', default=LAST, required=False, type=str,
	                        help="Set docker images version in the form `x[.x]`. Given `NEXT/PREV/LAST` compute version based on cache in .images_versions_used. ")

	mainParser.set_defaults(config_task=None)
	mainParser.set_defaults(custom_task=None)
	mainParser.set_defaults(main_task=None)
	mainParser.set_defaults(DO_RELOAD=False)

	main(mainParser, sys.argv[1:])
