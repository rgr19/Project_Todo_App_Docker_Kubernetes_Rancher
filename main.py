#!/usr/bin/env python3.7
import argparse
import logging
import os
import re
import sys
from pprint import pprint
from types import GeneratorType

import coloredlogs

from handlers.bin.aws import Aws
from handlers.bin.docker_compose import DockerCompose
from handlers.bin.helm import Helm
from handlers.bin.travis import Travis

NEXT = 'NEXT'
LAST = 'LAST'
PREV = 'PREV'


def parse_project_version(version: str):
    cacheFile = '.project_versions_used'
    versionPattern = r'^\d+(=?\.(\d+(=?\.(\d+)?)?)?)?$'
    regexMatcher = re.compile(versionPattern, flags=0)
    if not os.path.exists(cacheFile):
        open(cacheFile, 'w').write('')
        prevVersions = set()
    else:
        prevVersions = open(cacheFile, 'r').read().strip()
        prevVersions = set(filter(bool, prevVersions.splitlines()))

    if version == NEXT or version == LAST or version == PREV:
        versionTuple = lastVersionTuple = (0, 0, 0)
        for x in range(100):
            for y in range(100):
                for z in range(100):
                    tempVersion = f'{x}.{y}.{z}'
                    if tempVersion not in prevVersions:
                        if version == PREV:
                            if z:
                                versionTuple = x, y, z - 1
                            elif y:
                                versionTuple = x, y - 1, z
                            elif x:
                                versionTuple = x - 1, y, z
                            else:
                                versionTuple = x, y, z
                        if version == NEXT:
                            versionTuple = x, y, z
                        elif version == LAST:
                            versionTuple = lastVersionTuple
                        break
                    lastVersionTuple = x, y, z
                else:
                    continue  # only executed if the inner loop did NOT break
                break  # only executed if the inner loop DID break
            else:
                continue  # only executed if the inner loop did NOT break
            break  # only executed if the inner loop DID break
        version = '.'.join(map(str, versionTuple))
    else:
        if not bool(regexMatcher.match(version)):
            raise ValueError("Project version do not match pattern x[.x]")

    prevVersions.add(version)
    with open(cacheFile, 'w') as fp:
        for v in prevVersions:
            print(v, file=fp)
    return version


def parse_images_version(version: str):
    cacheFile = '.images_versions_used'
    versionPattern = r'^\d+(=?\.(\d+))?$'
    regexMatcher = re.compile(versionPattern, flags=0)
    versionTuple = lastVersionTuple = (0, 0, 0)

    if not os.path.exists(cacheFile):
        open(cacheFile, 'w').write('')
        prevVersions = set()
    else:
        prevVersions = open(cacheFile, 'r').read().strip()
        prevVersions = set(filter(bool, prevVersions.splitlines()))

    if version == NEXT or version == LAST or version == PREV:
        for x in range(100):
            for y in range(100):
                tempVersion = f'{x}.{y}'
                if tempVersion not in prevVersions:
                    if tempVersion == PREV:
                        if y:
                            versionTuple = x, y - 1
                        elif x:
                            versionTuple = x - 1, y
                        else:
                            versionTuple = x, y
                    if version == NEXT:
                        versionTuple = x, y
                    elif version == LAST:
                        versionTuple = lastVersionTuple
                    break
                lastVersionTuple = x, y
            else:
                continue  # only executed if the inner loop did NOT break
            break  # only executed if the inner loop DID break
        version = '.'.join(map(str, versionTuple))
    else:
        if not bool(regexMatcher.match(version)):
            raise ValueError("Project version do not match pattern x[.x]")

    prevVersions.add(version)
    with open(cacheFile, 'w') as fp:
        for v in prevVersions:
            print(v, file=fp)
    return version


class SetupParserTasks(object):

    def __init__(self, parser):
        # construct the argument parser and parse the arguments
        self.mainParser = parser

        self.operationParsers = self.mainParser.add_subparsers(dest='OPERATION', required=True,
                                                               description="Todo App operations selector.")
        self.setup_helm_parser()
        self.setup_docker_compose_parser()
        self.setup_travis_parser()
        self.setup_aws_parser()
        self.setup_kompose_parser()
        self.setup_k8s_parser()
        self.setup_automate()

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

    def setup_aws_parser(self):
        aws = self.operationParsers.add_parser("AWS", aliases=['A'], )
        aws.add_argument("-a", "--aws-app-env", dest='AWS_APP_ENV', type=str, required=False)
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
        travis.add_argument("-m", "--git-message", dest='GIT_MESSAGE', type=str, required=False)
        travis.set_defaults(config_task=Travis.main)

        tasks = travis.add_subparsers(dest='TASK', required=True, )

        task = tasks.add_parser("BASIC", aliases=['B'], )
        task.set_defaults(main_task=Travis.basic)

        task = tasks.add_parser("AWS", aliases=['A'], )
        task.set_defaults(main_task=Travis.aws)

    def setup_kompose_parser(self):
        argsKompose = self.operationParsers.add_parser("KOMPOSE", aliases=['k'], )

    def setup_k8s_parser(self):
        argsK8s = self.operationParsers.add_parser("K8S", aliases=['K'], )

    def setup_automate(self, ):
        automate = self.operationParsers.add_parser("AUTOMATE", aliases=['a'], )
        automate.set_defaults(config_task=[DockerCompose.main, Travis.main, Helm.main])
        automate.set_defaults(main_task=[DockerCompose.build, Travis.basic, Helm.reinstall])
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
    logger = logging.getLogger(__name__)

    infoFormat = "%(asctime)s,%(msecs)03d [%(hostname)s] [%(process)d] [%(programname)s.%(name)s:%(lineno)d] %(levelname)s => %(message)s"
    coloredlogs.install(level='INFO', fmt=infoFormat, )

    mainParser = argparse.ArgumentParser(prog="MAIN", description="Project Main CLI.")
    mainParser.add_argument('-d', '--dry-run', dest='DRY_RUN', default=False, required=False, action='store_true')
    mainParser.add_argument('-b', '--build-type', dest='BUILD_TYPE', default='prod', required=False, choices='DEV PROD'.split())
    mainParser.add_argument('-p', '--project-name', dest='PROJECT_NAME', default='todo-app', required=False)
    mainParser.add_argument('-e', '--envfiles-dir', dest='DIR_ENVFILES', default='.envfiles', required=False)
    mainParser.add_argument('-s', '--secretfiles-dir', dest='DIR_SECRETFILES', default='.secretfiles', required=False)

    mainParser.add_argument("-v", "--project-version", dest='PROJECT_VERSION', default=LAST, required=False, type=str,
                            help="Set project version in the form `x[.x[.x]]`. "
                                 "Given `NEXT/PREV/LAST` compute version based on cache in .chart_versions_used.")
    mainParser.add_argument("-V", "--images-version", dest='IMAGES_VERSION', default=LAST, required=False, type=str,
                            help="Set docker images version in the form `x[.x]`. "
                                 "Given `NEXT/PREV/LAST` compute version based on cache in .images_versions_used. ")

    mainParser.set_defaults(config_task=None)
    mainParser.set_defaults(custom_task=None)
    mainParser.set_defaults(main_task=None)
    mainParser.set_defaults(DO_RELOAD=False)

    main(mainParser, sys.argv[1:])
