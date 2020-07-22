#!/usr/bin/env python3.7.7

from handlers.lib.DockerCompose import DockerComposeConfigurator, DockerComposeExecutor
from handlers.lib.Logger import Logger

logger = Logger.build(__name__)


class DockerCompose(DockerComposeConfigurator):

	@staticmethod
	def run(*runArgs, **configurationKwargs):
		logger.info(f'{__class__.__name__}.run')
		DockerComposeExecutor(**configurationKwargs).run(*runArgs)

	@staticmethod
	def build(*runArgs, **configurationKwargs):
		logger.info(f'{__class__.__name__}.build')
		DockerComposeExecutor(**configurationKwargs).build(*runArgs)

	@staticmethod
	def up(*runArgs, **configurationKwargs):
		logger.info(f'{__class__.__name__}.up')
		DockerComposeExecutor(**configurationKwargs).up(*runArgs)

	@staticmethod
	def up_detach(*runArgs, **configurationKwargs):
		logger.info(f'{__class__.__name__}.up')
		DockerComposeExecutor(**configurationKwargs).up_detach(*runArgs)

	@staticmethod
	def down(*runArgs, **configurationKwargs):
		logger.info(f'{__class__.__name__}.down')
		DockerComposeExecutor(**configurationKwargs).down(*runArgs)

	@staticmethod
	def kill(**configurationKwargs):
		logger.info(f'{__class__.__name__}.kill')
		DockerComposeExecutor(**configurationKwargs).kill()

	@staticmethod
	def pull(*runArgs, **configurationKwargs):
		logger.info(f'{__class__.__name__}.pull')
		DockerComposeExecutor(**configurationKwargs).pull(*runArgs)

	@staticmethod
	def push(*runArgs, **configurationKwargs):
		logger.info(f'{__class__.__name__}.pull')
		DockerComposeExecutor(**configurationKwargs).push(*runArgs)

	@staticmethod
	def logs(*runArgs, **configurationKwargs):
		logger.info(f'{__class__.__name__}.logs')
		DockerComposeExecutor(**configurationKwargs).logs(*runArgs)

	@staticmethod
	def logs_follow(*runArgs, **configurationKwargs):
		logger.info(f'{__class__.__name__}.logs')
		DockerComposeExecutor(**configurationKwargs).logs_follow(*runArgs)

	@staticmethod
	def install(**configurationKwargs):
		logger.info(f'{__class__.__name__}.install')
		doReload: bool = configurationKwargs['DO_RELOAD']
		configurationKwargs['DO_RELOAD'] = False
		DockerCompose.down(**configurationKwargs)
		configurationKwargs['DO_RELOAD'] = doReload
		DockerCompose.pull(**configurationKwargs)
		configurationKwargs['DO_RELOAD'] = False
		DockerCompose.build(**configurationKwargs)
		DockerCompose.up_detach(**configurationKwargs)
