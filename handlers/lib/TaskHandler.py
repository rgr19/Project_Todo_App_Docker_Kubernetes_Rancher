import argparse

import logging

logger = logging.getLogger(__name__)


class TaskHandler(argparse.Action):

    TASKSET='taskset'

    def __init__(self, option_strings, dest, nargs=0, const=True, default=True, required=False, *args, **kwargs):
        logger.debug(f'[INIT][{dest}] OPTION_STRING: {option_strings}, ARGS: {args}, KWARGS: {kwargs}, DEFAULT={default}')
        super().__init__(
            option_strings, dest, nargs=nargs, const=const, default=default, required=required, **kwargs
        )

    def __call__(self, parser, namespace, values, option_string=None):
        logger.debug(f'[CALL][{parser}] NAMESPACE: {namespace} => VALUES: {values} => OPTION_STRING: {option_string}')
        setattr(namespace, self.dest, self.const)
