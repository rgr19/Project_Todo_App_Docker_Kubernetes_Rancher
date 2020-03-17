#!/usr/bin/env python3.7.7

from handlers.lib.Executor import Executor, ExecutorAbstract
from handlers.lib.Logger import Logger

logger = Logger.build(__name__)


class GitExecutor(ExecutorAbstract):
	GIT: str = 'git'
	REV_PARSE: str = 'rev-parse'
	ABBREV_REF: str = 'abbrev-ref'
	HEAD: str = 'HEAD'
	CONFIG: str = 'config'
	CHECKOUT: str = 'checkout'
	USER_NAME: str = 'user.name'
	ADD: str = 'add'
	ALL: str = 'all'
	COMMIT: str = 'commit'
	MESSAGE: str = 'message'
	PUSH: str = 'push'
	ORIGIN: str = 'origin'
	MASTER: str = 'master'
	GH_PAGES: str = 'gh-pages'

	def __init__(self, cwd: str = None):
		self.cwd = cwd

	def __call__(self, subcommand=None) -> Executor:
		return Executor(self.GIT).with_subcommand(subcommand).with_cwd(self.cwd)

	def checkout_branch(self, branch):
		logger.debug(f'{__class__.__name__}.checkout_branch')
		return self(self.CHECKOUT).with_args(branch).exec()

	def branch(self):
		logger.debug(f'{__class__.__name__}.branch')
		return self(self.REV_PARSE).with_kwarg(self.ABBREV_REF, self.HEAD).exec()

	def user_name(self):
		logger.debug(f'{__class__.__name__}.user_name')
		return self(self.CONFIG).with_args(self.USER_NAME).exec()

	def add_all(self):
		logger.debug(f'{__class__.__name__}.add_all')
		self(self.ADD).with_flags(self.ALL).spawn()

	def commit_msg(self, msg: str, *_):
		logger.debug(f'{__class__.__name__}.commit_msg => MSG : {msg}')
		self(self.COMMIT).with_kwarg(self.MESSAGE, msg).spawn()

	def push_origin(self):
		branch: str = self.branch()
		logger.debug(f'{__class__.__name__}.push_origin => BRANCH: {branch}')
		self(self.PUSH).with_args(self.ORIGIN, branch).spawn()

	def upload(self, gitMessage: str = None, ):
		logger.debug(f'{__class__.__name__}.upload GIT_MESSAGE => {gitMessage}')
		self.add_all()
		self.commit_msg(gitMessage)
		self.push_origin()
