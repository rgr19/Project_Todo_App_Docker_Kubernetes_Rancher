#!/usr/bin/env python3.7

import abc
import logging
import subprocess
from typing import Union

logger = logging.getLogger(__name__)

logger.info("Hello logging!")


class ExecutorOutputParser(object):
    stdout: str = ''
    stderr: str = ''

    def __init__(self, stdout, stderr, returncode):
        if stdout:
            self.stdout = stdout.decode("utf-8")
        if stderr:
            self.stderr = stderr.decode("utf-8")
        self.returncode = returncode

    def get_all(self):
        return self.stdout, self.stderr, self.returncode

    def get_as_list(self):
        return self.stdout.splitlines()

    def get(self):
        return self.stdout

    def print(self):

        if not self.stdout and not self.stderr:
            print("STDOUT => None")
            print("STDERR => None")
            return

        if self.stdout:
            print("#" * 100)
            print("#### STDOUT : ")
            print("#" * 100)
            print(self.stdout)
            print("#" * 100)
            print()
        if self.stderr:
            print("#" * 100)
            print("#### STDERR :")
            print("#" * 100)
            print(self.stderr)
            print("#" * 100)
            print()


class Executor(object):

    def __init__(self, *command: str):
        self.cmd: list = []
        self.cwd: Union[None, str] = None
        self.with_command(command)

    def with_command(self, command):
        self.cmd: list = []
        if isinstance(command, (list, tuple, set)):
            self.cmd.extend(command)
        elif isinstance(command, str):
            self.cmd.append(command)
        else:
            raise TypeError(f"Wrong type for 'command' : {command}")
        return self

    def with_subcommand(self, subcommand=None):
        if subcommand:
            self.cmd.append(subcommand)
        return self

    def with_cwd(self, cwd):
        self.cwd = cwd
        return self

    def with_args(self, *args):
        for arg in args:
            for split in arg.split():
                self.cmd.append(split)
        return self

    def with_kwargs(self, **kwargs):
        for k, v in kwargs.items():
            self.with_kwarg(k, v)
        return self

    def with_envvars(self, **envvars):
        for env, var in envvars.items():
            self.with_envvar(env, var)
        return self

    def with_kwarg(self, key, val):
        self.cmd.append(f'--{key}')
        self.cmd.append(val)
        return self

    def with_envvar(self, env, var):
        self.cmd.append(f'{env}={var}')

    def with_flags(self, *flags):
        for arg in flags:
            self.cmd.append(f'--{arg}')
        return self

    def exec(self, ) -> ExecutorOutputParser:
        logger.info(f'{self.__class__.__name__} begin EXEC : {self.cmd} in CWD: {self.cwd}')
        if not self.cmd:
            raise Exception(f"No command provided CMD: {self.cmd}")
        try:
            process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.cwd)
            stdout, stderr = process.communicate()
            logger.info(f'{self.__class__.__name__} end EXEC : {self.cmd} in CWD: {self.cwd}')
            if process.returncode:
                logger.error(f"Subprocess returned with exitcode {process.returncode}")
            return ExecutorOutputParser(stdout, stderr, process.returncode)
        except KeyboardInterrupt:
            logger.error(f'{self.__class__.__name__} keyboard interrupt in EXEC : {self.cmd} in CWD: {self.cwd}')

    def spawn(self) -> int:
        logger.info(f'{self.__class__.__name__} begin SPAWN : {self.cmd} in CWD: {self.cwd}')
        if not self.cmd:
            raise Exception(f"No command provided CMD: {self.cmd}")
        try:
            returncode = subprocess.check_call(self.cmd, cwd=self.cwd)
            logger.info(f'{self.__class__.__name__} end EXEC')
            if returncode:
                logger.error(f"Subprocess returned with exitcode {returncode}")
            return returncode
        except KeyboardInterrupt:
            logger.error(f'{self.__class__.__name__} keyboard interrupt in SPAWN : {self.cmd} in CWD: {self.cwd}')


class ExecutorAbstract(abc.ABC):

    @abc.abstractmethod
    def __call__(self, subcommand: str = None) -> Executor:
        pass
