#!/usr/bin/env python3.7

import abc
import os
import subprocess
from typing import Union

from handlers.lib.Logger import Logger

logger = Logger.build(__name__)


class ExecutorOutputParser(object):
	stdout: str = ''
	stderr: str = ''

	def __init__(self, stdout=b'', stderr=b'', returncode=0):
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
			print("=" * 50, " STDOUT ", "=" * 50)
			print(self.stdout)
			print("=" * 110)
		if self.stderr:
			print("=" * 50, " STDERR ", "=" * 50)
			print(self.stderr)
			print("=" * 110)


class Executor(object):

	def __init__(self, command: Union[list, tuple, set, str]):
		self.cmd: list = []
		self.cwd: Union[None, str] = None
		self.with_command(command)

	def with_command(self, command: Union[list, tuple, set, str]):
		self.cmd: list = []
		if isinstance(command, (list, tuple, set)):
			self.cmd.extend(command)
		elif isinstance(command, str):
			self.cmd.append(command)
		else:
			raise TypeError(f"Wrong type for 'command' : {command}")
		return self

	def with_subcommand(self, subcommand: str = None):
		if subcommand:
			self.cmd.append(subcommand)
		return self

	def with_cwd(self, cwd):
		if cwd:
			self.cwd = cwd
		return self

	def with_args(self, *args):
		for arg in args:
			if not arg:
				continue
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

	def exec(self, doUntilOk=False, exitOnError=True) -> str:
		logger.info(f'{self.__class__.__name__} begin EXEC : {self.cmd} in CWD: {self.cwd}')
		if not self.cmd:
			logger.exception(f"No command provided CMD: {self.cmd}")
			exit(1)
		try:
			if os.environ['DRY_RUN']:
				out = ExecutorOutputParser(b'DRY_RUN')
			else:
				process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.cwd)
				stdout, stderr = process.communicate()
				out = ExecutorOutputParser(stdout, stderr, process.returncode)
				out.print()
				if doUntilOk and out.returncode:
					logger.error(f"Subprocess failed with returncode: {out.returncode}. Try again...")
					self.exec(doUntilOk, exitOnError)
				if out.returncode:
					logger.exception(f"Subprocess returned with exitcode {out.returncode}")
					if exitOnError:
						exit(2)
			logger.info(f'{self.__class__.__name__} end EXEC : {self.cmd} in CWD: {self.cwd}')
			return out.get()

		except KeyboardInterrupt:
			logger.exception(f'{self.__class__.__name__} keyboard interrupt in EXEC : {self.cmd} in CWD: {self.cwd}')
			exit(3)

	def spawn(self, doUntilOk=False, exitOnError=True) -> None:
		logger.info(f'{self.__class__.__name__} begin SPAWN : {self.cmd} in CWD: {self.cwd}')
		if not self.cmd:
			logger.exception(f"No command provided CMD: {self.cmd}")
			exit(1)
		if not os.environ['DRY_RUN']:
			try:
				returncode = subprocess.check_call(self.cmd, cwd=self.cwd)
				out = ExecutorOutputParser(returncode=returncode)
				out.print()
				if returncode:
					logger.exception(f"Subprocess returned with exitcode {returncode}")
					if exitOnError:
						exit(2)
					elif doUntilOk:
						logger.error(f"Subprocess failed spawn with exitcode {returncode}. Try again...")
						self.spawn(doUntilOk, exitOnError)
			except KeyboardInterrupt:
				logger.exception(f'{self.__class__.__name__} keyboard interrupt in SPAWN : {self.cmd} in CWD: {self.cwd}')
				exit(4)
			except subprocess.CalledProcessError as err:
				if exitOnError:
					logger.exception(err)
					exit(3)
				logger.error(f"Subprocess failed spawn. Try again...")
				if doUntilOk:
					self.spawn(doUntilOk, exitOnError)

		logger.info(f'{self.__class__.__name__} end SPAWN : {self.cmd} in CWD: {self.cwd}')


class ExecutorAbstract(abc.ABC):

	@abc.abstractmethod
	def __call__(self, subcommand: str = None) -> Executor:
		pass
