#!/usr/bin/env python3.7
import argparse
import logging
import sys
from types import GeneratorType

import coloredlogs

from handlers.bin.aws import Aws
from handlers.bin.docker_compose import DockerCompose
from handlers.bin.helm import Helm
from handlers.bin.travis import Travis
from handlers.lib.Executor import ExecutorOutputParser


class SetupActions(object):

    def __init__(self, parser):
        # construct the argument parser and parse the arguments
        self.mainParser = parser

        self.operationParsers = self.mainParser.add_subparsers(dest='OPERATION', required=True, description="Todo App operations selector.")
        self.setup_helm_parser()
        self.setup_docker_compose_parser()
        self.setup_travis_parser()
        self.setup_aws_parser()
        self.setup_kompose_parser()
        self.setup_k8s_parser()

    def setup_docker_compose_parser(self):
        epilog = 'Note: Helm values.yaml will be converted to .env.helm and used.'
        dockerCompose = self.operationParsers.add_parser("DOCKER_COMPOSE", aliases=['DC'], epilog=epilog)
        dockerCompose.set_defaults(config_task=DockerCompose.main)
        dockerCompose.set_defaults(DO_RELOAD=False)

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

    def setup_aws_parser(self):
        aws = self.operationParsers.add_parser("AWS", aliases=['A'], )
        aws.add_argument("-a", "--aws-app-env", dest='AWS_APP_ENV', type=str, required=False)
        aws.set_defaults(config_task=Aws.main, )

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
        travis.add_argument("-m", "--git-message", dest='GIT_MESSAGE', type=str, required=False)
        travis.set_defaults(config_task=Travis.main, )

        tasks = travis.add_subparsers(dest='TASK', required=True, )

        task = tasks.add_parser("BASIC", aliases=['B'], )
        task.set_defaults(main_task=Travis.basic)

        task = tasks.add_parser("AWS", aliases=['A'], )
        task.set_defaults(main_task=Travis.aws)

    def setup_kompose_parser(self):
        argsKompose = self.operationParsers.add_parser("KOMPOSE", aliases=['k'], )

    def setup_k8s_parser(self):
        argsK8s = self.operationParsers.add_parser("K8S", aliases=['K'], )

    def parse_args(self, argv, ):
        return self.mainParser.parse_args(argv, )


def main(parser, argv):
    logger.info(f' main : {argv}')
    SetupActions(parser)
    parsedArgs, customArgs = parser.parse_known_args(argv)
    print(parsedArgs)
    print(customArgs)
    kwargsDict = vars(parsedArgs)

    config_task = kwargsDict.pop('config_task')
    main_task = kwargsDict.pop('main_task')

    if config_task:
        config_task(**kwargsDict)

    if main_task:
        if isinstance(main_task, list):
            if len(main_task) == 2:
                main_task, taskArgs = main_task
            else:
                main_task, taskArgs = main_task[0], tuple()
            out = main_task(*taskArgs, *customArgs, **kwargsDict)
        else:
            out = main_task(*customArgs, **kwargsDict)

        if isinstance(out, ExecutorOutputParser):
            out.print()
        elif isinstance(out, GeneratorType):
            for genOut in out:
                if isinstance(genOut, ExecutorOutputParser):
                    genOut.print()


if __name__ == '__main__':
    logger = logging.getLogger(__name__)

    infoFormat = "%(asctime)s,%(msecs)03d [%(hostname)s] [%(process)d] [%(programname)s.%(name)s:%(lineno)d] %(levelname)s => %(message)s"
    coloredlogs.install(level='INFO', fmt=infoFormat, )

    mainParser = argparse.ArgumentParser(prog="MAIN", description="Project Main CLI.")
    mainParser.add_argument('-b', '--build-type', dest='BUILD_TYPE', default='prod', required=False, choices='DEV PROD'.split())
    mainParser.add_argument('-p', '--project-name', dest='PROJECT_NAME', default='todo-app', required=False)
    mainParser.add_argument('-e', '--envfiles-dir', dest='DIR_ENVFILES', default='.envfiles', required=False)
    mainParser.add_argument('-s', '--secretfiles-dir', dest='DIR_SECRETFILES', default='.secretfiles', required=False)
    mainParser.add_argument("-v", "--project-version", dest='PROJECT_VERSION', default="0.0.0", required=False, help="Set project version.")

    mainParser.set_defaults(config_task=None)
    mainParser.set_defaults(custom_task=None)
    mainParser.set_defaults(main_task=None)
    mainParser.set_defaults(DO_RELOAD=False)

    main(mainParser, sys.argv[1:])
