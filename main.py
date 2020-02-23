#!/usr/bin/env python3
import logging
import os
import sys
import coloredlogs, logging
import traceback

import argparse
from pprint import pprint

import inspect

import multiline_formatter.formatter

from handlers.lib.RainbowStreamHandler import RainbowStreamHandler
from handlers.bin.helm import Helm
from handlers.bin.docker import Docker


class SetupActions(object):

    def __init__(self, mainParser):
        # construct the argument parser and parse the arguments
        self.mainParser = mainParser

        self.operationParsers = self.mainParser.add_subparsers(dest='OPERATION', required=False, description="Todo App operations selector.")
        self.setup_docker_parser()
        self.setup_travis_parser()
        self.setup_aws_parser()
        self.setup_kompose_parser()
        self.setup_k8s_parser()
        self.setup_helm_parser()

    def setup_helm_parser(self, ):
        helm = self.operationParsers.add_parser("HELM", aliases=['H'], )
        helm.add_argument("-v", "--version", required=False, help="Override version.", default="0.0.0")

        helm.add_argument("--main", dest='main', default=Helm.main)

        task = helm.add_subparsers(dest='TASK', required=True, )

        taskLint = task.add_parser("LINT", aliases=['L'], )
        taskLint.add_argument("--lint", dest='task', default=Helm.lint)

        taskTemplate = task.add_parser("TEMPLATE", aliases=['T'])
        taskTemplate.add_argument("--template", dest='task', default=Helm.template)

        taskDryRun = task.add_parser("DRY-RUN", aliases=['D'])
        taskDryRun.add_argument("--dry-run", dest='task', default=Helm.dry_run)

        taskDryRun = task.add_parser("FULL_CHECK", aliases=['F'])
        taskDryRun.add_argument("--full-check", dest='task', default=Helm.full_check)

        taskInstall = task.add_parser("INSTALL", aliases=['I'])
        taskInstall.add_argument("--install", dest='task', default=Helm.install)

    def setup_docker_parser(self):
        docker = self.operationParsers.add_parser("DOCKER", aliases=['D'], )

        runtype = docker.add_subparsers(dest='RUNTYPE', required=True, )
        runtypeProd = runtype.add_parser("PROD", aliases=['P'], )
        runtypeProd.add_argument("prod", action=Docker.Prod)
        runtypeDev = runtype.add_parser("DEV", aliases=['D'], )
        runtypeDev.add_argument("dev", action=Docker.Dev)

    def setup_travis_parser(self):
        travis = self.operationParsers.add_parser("TRAVIS", aliases=['T'], )

        runtype = travis.add_subparsers(dest='RUNTYPE', required=True, )
        runtypeBasic = runtype.add_parser("NONE", aliases=['N'], )
        runtypeAws = runtype.add_parser("AWS", aliases=['A'], )
        runtypeK8s = runtype.add_parser("K8S", aliases=['K'], )
        runtypeHelm = runtype.add_parser("HELM", aliases=['H'], )

    def setup_aws_parser(self):
        argsAws = self.operationParsers.add_parser("AWS", aliases=['A'], )

    def setup_kompose_parser(self):
        argsKompose = self.operationParsers.add_parser("KOMPOSE", aliases=['k'], )

    def setup_k8s_parser(self):
        argsK8s = self.operationParsers.add_parser("K8S", aliases=['K'], )

    def parse_args(self, argv, ):
        return self.mainParser.parse_args(argv, )


def main(mainParser, argv):
    logger.info(f' main : {argv}')
    SetupActions(mainParser)
    parsedArgs = mainParser.parse_args(argv, )
    argsDict = vars(parsedArgs)

    main = argsDict.pop('main')
    task = argsDict.pop('task')

    main(**argsDict)
    task(**argsDict)

    return argsDict, parsedArgs


#
# def exception_handler(type, value, tb):
#     logger.error(f"Uncaught exception: {value}, TYPE:{type} TB:")
#     print(traceback.extract_tb(tb))
#
# # Install exception handler
# sys.excepthook = exception_handler

if __name__ == '__main__':

    logger = logging.getLogger(__name__)
    # By default the install() function installs a handler on the root logger,
    # this means that log messages from your code and log messages from the
    # libraries that you use will all show up on the terminal.

    # exceptionFormatter = multiline_formatter.formatter.MultilineMessagesFormatter('[%(levelname)s] %(message)s')
    # errorHandler = logging.StreamHandler(sys.stderr)
    # errorHandler.setFormatter(exceptionFormatter)
    # errorHandler.setLevel(logging.ERROR)
    #
    # logger.addHandler(errorHandler)
    infoFormat = "%(asctime)s,%(msecs)03d [%(hostname)s] [%(process)d] [%(programname)s.%(name)s:%(lineno)d] %(levelname)s => %(message)s"
    coloredlogs.install(level='INFO', fmt=infoFormat, )
    # Create a logger object.

    mainParser = argparse.ArgumentParser(prog="MAIN", description="Project Main CLI.", conflict_handler='resolve')
    mainParser.add_argument('-b', '--build-type', dest='BUILD_TYPE', type=str, default='prod', required=False)
    mainParser.add_argument('-p', '--project-name', dest='PROJECT_NAME', type=str, default='todo-app', required=False)

    argsDict, parsedArgs = main(mainParser, sys.argv[1:])
