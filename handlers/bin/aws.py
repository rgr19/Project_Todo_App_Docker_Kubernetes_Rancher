#!/usr/bin/env python3.7
import logging

from handlers.lib.Aws import AwsConfigurator, AwsExecutor
from handlers.lib.Logger import Logger

logger = Logger.build(__name__)



class Aws(AwsConfigurator):

	@staticmethod
	def run(*runArgs, **configurationKwargs):
		logger.info(f'{__class__.__name__}.run')
		return AwsExecutor(**configurationKwargs).run(*runArgs)

	@staticmethod
	def setenv(*runArgs, **configurationKwargs):
		logger.info(f'{__class__.__name__}.setenv')
		return AwsExecutor(**configurationKwargs).run(*runArgs)

	@staticmethod
	def use(*runArgs, **configurationKwargs):
		logger.info(f'{__class__.__name__}.setenv')
		return AwsExecutor(**configurationKwargs).use(*runArgs)

	@staticmethod
	def list(*runArgs, **configurationKwargs):
		logger.info(f'{__class__.__name__}.setenv')
		return AwsExecutor(**configurationKwargs).list(*runArgs)
