#!/usr/bin/env python3
import os

from handlers.lib.TaskHandler import TaskHandler
import logging

logger = logging.getLogger(__name__)

logger.info("Hello logging!")


class Helm(object):
    HELM = 'helm'
    TASKSET = 'taskset'
    HELM_PATH = os.path.join(TASKSET, HELM)

    @staticmethod
    def install(*args, **kwargs):
        logger.info(f'ARGS: {args}, KWARGS: {kwargs}')

    @staticmethod
    def lint(*args, **kwargs):
        logger.info(f'ARGS: {args}, KWARGS: {kwargs}')

    @staticmethod
    def template(*args, **kwargs):
        logger.info(f'ARGS: {args}, KWARGS: {kwargs}')


    @staticmethod
    def dry_run(*args, **kwargs):
        logger.info(f'ARGS: {args}, KWARGS: {kwargs}')

    @staticmethod
    def full_check(*args, **kwargs):
        logger.info(f'ARGS: {args}, KWARGS: {kwargs}')
        Helm.lint(*args, **kwargs)
        Helm.template(*args, **kwargs)
        Helm.dry_run(*args, **kwargs)

    @staticmethod
    def override_version(*args, **kwargs):
        logger.info(f'ARGS: {args}, KWARGS: {kwargs}')

    @staticmethod
    def main(*args, **kwargs):
        logger.info(f'ARGS: {args}, KWARGS: {kwargs}')
        for root, dirs, files in os.walk(Helm.TASKSET):
            print(root, dirs, files)
