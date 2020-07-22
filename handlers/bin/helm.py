#!/usr/bin/env python3.7.7

from handlers.lib.Helm import HelmConfigurator, HelmExecutor
from handlers.lib.Logger import Logger

logger = Logger.build(__name__)


class Helm(HelmConfigurator):

	@staticmethod
	def run(*args, **configurationKwargs):
		logger.info(f'{__class__.__name__}.run')
		HelmExecutor(**configurationKwargs).run(*args)

	@staticmethod
	def install(**configurationKwargs):
		logger.info(f'{__class__.__name__}.install')
		HelmExecutor(**configurationKwargs).install()

	@staticmethod
	def uninstall(**configurationKwargs):
		logger.info(f'{__class__.__name__}.uninstall')
		try:
			HelmExecutor(**configurationKwargs).uninstall()
		except Exception as err:
			logger.exception(f'{__class__.__name__}.uninstall FAILED due to {err}')
			pass

	@staticmethod
	def upgrade(**configurationKwargs):
		logger.info(f'{__class__.__name__}.upgrade')
		HelmExecutor(**configurationKwargs).upgrade()

	@staticmethod
	def reinstall(**configurationKwargs):
		logger.info(f'{__class__.__name__}.reinstall')

		doReload = configurationKwargs['DO_RELOAD']
		configurationKwargs['DO_RELOAD'] = False
		HelmExecutor(**configurationKwargs).uninstall()
		configurationKwargs['DO_RELOAD'] = doReload
		HelmExecutor(**configurationKwargs).install(doUntilOk=True)

	@staticmethod
	def dry_run(**configurationKwargs):
		logger.info(f'{__class__.__name__}.dry_run')
		HelmExecutor(**configurationKwargs).dry_run()

	@staticmethod
	def lint(**configurationKwargs):
		logger.info(f'{__class__.__name__}.lint')
		HelmExecutor(**configurationKwargs).lint()

	@staticmethod
	def template(**configurationKwargs):
		logger.info(f'{__class__.__name__}.template')
		HelmExecutor(**configurationKwargs).template()

	@staticmethod
	def full_check(**configurationKwargs):
		logger.info(f'{__class__.__name__}.full_check')
		Helm.lint(**configurationKwargs)
		Helm.template(**configurationKwargs)
		Helm.dry_run(**configurationKwargs)
