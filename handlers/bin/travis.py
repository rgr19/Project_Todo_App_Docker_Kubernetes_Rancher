#!/usr/bin/env python3.7.7
from pprint import pprint

from handlers.lib.Helm import HelmExecutor
from handlers.lib.Logger import Logger
from handlers.lib.Travis import TravisConfigurator, TravisExecutor, TravisTasks

logger = Logger.build(__name__)


class Travis(TravisConfigurator):

	@staticmethod
	def logs(**configurationKwargs):
		logger.info(f'{__class__.__name__}.logs')
		TravisExecutor(**configurationKwargs).logs()

	@staticmethod
	def basic(gitMessage: str = None, *secrets: str, **configurationKwargs):
		logger.info(f'{__class__.__name__}.basic')
		TravisExecutor(TravisTasks.Base, **configurationKwargs).task(gitMessage, *secrets)

	@staticmethod
	def aws(gitMessage: str = None, *secrets: str, **configurationKwargs):
		logger.info(f'{__class__.__name__}.aws')
		TravisExecutor(TravisTasks.Base, TravisTasks.Aws, **configurationKwargs).task(gitMessage, *secrets)

	@staticmethod
	def encrypt(*secrets: str, **configurationKwargs):
		logger.info(f'{__class__.__name__}.encrypt')
		TravisExecutor(**configurationKwargs).encrypt(*secrets)


class TravisSubmodule(TravisConfigurator):
	@staticmethod
	def helm(gitMessage: str = None, *secrets: str, **configurationKwargs):
		logger.info(f'{__class__.__name__}.helm')
		pprint(configurationKwargs)
		helm = HelmExecutor(**configurationKwargs)
		helm.main(**configurationKwargs)
		helm.dry_run()
		TravisExecutor(TravisTasks.HelmRepo, destPath=helm.repoPath, **configurationKwargs).task(gitMessage, *secrets)
