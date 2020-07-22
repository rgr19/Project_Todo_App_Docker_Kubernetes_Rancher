import collections
import logging

import coloredlogs


class Logger(object):
	level = 'INFO'

	@staticmethod
	def set_level(level):
		Logger.level = level
		return Logger

	@staticmethod
	def build(name):
		loggerFormat = collections.OrderedDict(
			dateTime="%(asctime)s,%(msecs)03d",
			hostname="[%(hostname)s]",
			process="[%(process)d]",
			code="[%(programname)s.%(name)s:%(lineno)d]",
			level="%(levelname)s",
			message="=> %(message)s",
		)
		loggerFormat = ' '.join(loggerFormat.values())
		coloredlogs.install(level=Logger.level, fmt=loggerFormat, )
		return logging.getLogger(name)
