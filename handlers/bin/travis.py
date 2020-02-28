#!/usr/bin/env python3.7.7
import os
from shutil import copyfile

from handlers.lib.Executor import Executor, ExecutorAbstract
from handlers.lib.FilesHandlers import YamlConcatWrite, EnvRead, Env, FileWrite
from handlers.lib.Taskset import TasksetConfig
from handlers.lib.common import *

logger = logging.getLogger(__name__)

logger.info("Hello logging!")


class TravisConfigurator(TasksetConfig):
    TRAVIS: str = 'travis'
    TRAVIS_YML: str = '.travis.yml'
    TRAVIS_BASE_YML: str = '.travis.base.yml'
    TRAVIS_AWS_YML: str = '.travis.aws.yml'

    BASE_SECRETS: set = {
        'DOCKER_HUB_PASSWORD',
        'DOCKER_HUB_ID',
        'GITHUB_BRANCH',
        'GITHUB_USER',
        'BUILD_TYPE',
    }

    AWS_SECRETS: set = {
        'AWS_SECRET_KEY',
        'AWS_KEY_ID'
    }

    TASK_MODE_BASIC = 'mode_basic'
    TASK_MODE_AWS = 'mode_aws'
    TASK_MODE_HELM = 'mode_helm'

    def __init__(self, **configurationVariables):
        super().__init__(**configurationVariables)
        logger.info(f'{__class__.__name__}.__init__')

        self.taskPath: str = os.path.join(self.PATH_TASKSET, self.TRAVIS)
        self.templatePath: str = os.path.join(self.taskPath, self.TEMPLATE)
        self.travisYmlPath: str = os.path.join(self.taskPath, self.TRAVIS_YML)

        self.cwdPath: str = self.taskPath

        self.taskYamlsUsed: list = []
        self.envVarsSecrets: list = []

        os.makedirs(self.taskPath, exist_ok=True)
        os.makedirs(self.templatePath, exist_ok=True)

    def save_github_config_to_envfiles(self, **configurationKwargs):
        logger.info(f'{__class__.__name__}.save_github_config_to_envfiles')
        if not configurationKwargs:
            logger.exception("Dict of `configurationKwargs` can not be empty.")
        gitBranch = GitExecutor(**configurationKwargs).branch()
        gitUserName = GitExecutor(**configurationKwargs).user_name()
        FileWrite(self.GITHUB_BRANCH_ENVFILE, gitBranch)
        FileWrite(self.GITHUB_USER_ENVFILE, gitUserName)
        return self

    def merge_travis_templates_to_root(self, taskMode: str = None):
        logger.info(f'{__class__.__name__}.copy_travis_templates_to_cwd')
        if not taskMode:
            logger.exception("Task mode can note be None.")

        templateTravisBaseYml = os.path.join(self.templatePath, self.TRAVIS_BASE_YML)
        templateTravisAwsYml = os.path.join(self.templatePath, self.TRAVIS_AWS_YML)
        rootTravisYml = self.TRAVIS_YML

        taskYamlsUsed: list = [templateTravisBaseYml]
        if taskMode == self.TASK_MODE_AWS:
            self.taskYamlsUsed.append(templateTravisAwsYml)

        YamlConcatWrite.as_is(self.travisYmlPath, *taskYamlsUsed)
        copyfile(self.travisYmlPath, rootTravisYml)

        return self

    def load_envvars_and_secrets(self, taskMode: str = None, *customSecrets: str):
        logger.info(f'{__class__.__name__}.load_envvars_and_secrets')
        if not taskMode:
            logger.exception("Task mode can note be None.")

        allSecrets = {}
        allSecrets.update(EnvRead.dir_to_dict(self.DIR_SECRETFILES))
        allSecrets.update(EnvRead.dir_to_dict(self.DIR_ENVFILES))

        for secret in customSecrets:
            k, v = secret.split('=')
            allSecrets[k] = v

        taskSecrets = {k: allSecrets[k] for k in self.BASE_SECRETS}
        if taskMode == self.TASK_MODE_AWS:
            for k in self.AWS_SECRETS:
                taskSecrets[k] = allSecrets[k]

        self.envVarsSecrets = Env.dict_to_env_lines(taskSecrets)

        return self

    @staticmethod
    def main(DO_RELOAD, **configurationKwargs):
        logger.info(f'{__class__.__name__}.main')

        travis = TravisConfigurator(**configurationKwargs)

        if DO_RELOAD:
            if travis.is_reloaded():
                return travis

            travis.save_github_config_to_envfiles(**configurationKwargs)

        return travis


class GitExecutor(ExecutorAbstract, TravisConfigurator):
    GIT: str = 'git'
    REV_PARSE: str = 'rev-parse'
    ABBREV_REF: str = 'abbrev-ref'
    HEAD: str = 'HEAD'
    CONFIG: str = 'config'
    USER_NAME: str = 'user.name'
    ADD: str = 'add'
    ALL: str = 'all'
    COMMIT: str = 'commit'
    MESSAGE: str = 'message'
    PUSH: str = 'push'
    ORIGIN: str = 'origin'

    def __call__(self, subcommand=None) -> Executor:
        return Executor(self.GIT).with_subcommand(subcommand)

    def branch(self):
        logger.info(f'{__class__.__name__}.branch')
        return self(self.REV_PARSE).with_kwarg(self.ABBREV_REF, self.HEAD).exec().get()

    def user_name(self):
        logger.info(f'{__class__.__name__}.user_name')
        return self(self.CONFIG).with_args(self.USER_NAME).exec().get()

    def add_all(self):
        logger.info(f'{__class__.__name__}.add_all')
        return self(self.ADD).with_flags(self.ALL).spawn()

    def commit_msg(self, msg: str, *_):
        logger.info(f'{__class__.__name__}.commit_msg => MSG : {msg}')
        return self(self.COMMIT).with_kwarg(self.MESSAGE, msg).spawn()

    def push_origin(self):
        branch: str = self.branch()
        logger.info(f'{__class__.__name__}.push_origin => BRANCH: {branch}')
        return self(self.PUSH).with_args(self.ORIGIN, branch).spawn()

    def task(self, taskMode, gitMsg: str = None, ):
        logger.info(f'{__class__.__name__}.main')
        if taskMode is None:
            logger.exception("Task mode can not be None.")
        if not gitMsg:
            gitMsg = f"Travis AUTO commit in MODE {taskMode}"

        self.add_all()
        self.commit_msg(gitMsg)
        self.push_origin()


class TravisExecutor(ExecutorAbstract, TravisConfigurator):
    TRAVIS: str = 'travis'
    ENCRYPT: str = 'encrypt'
    ADD: str = 'add'
    ENV_GLOBAL: str = 'env.global'
    OVERRIDE: str = 'override'
    ORG: str = 'org'

    def __call__(self, subcommand: str = None) -> Executor:
        return Executor(self.TRAVIS).with_cwd(self.cwdPath).with_subcommand(subcommand)

    def encrypt(self, *secrets):
        logger.info(f'{__class__.__name__}.')
        self(self.ENCRYPT).with_args(*secrets).with_kwarg(self.ADD, self.ENV_GLOBAL).with_flags(self.OVERRIDE, self.ORG).spawn()

    def basic(self):
        logger.info(f'{__class__.__name__}.')

    def aws(self):
        logger.info(f'{__class__.__name__}.')

    def task(self, taskMode, *secrets: str):
        logger.info(f'{__class__.__name__}.main')

        self.merge_travis_templates_to_root(taskMode)
        self.load_envvars_and_secrets(taskMode, *secrets)
        self.encrypt(*self.envVarsSecrets)


class Travis(TravisConfigurator):

    @staticmethod
    def basic(gitMsg: str = None, *secrets: str, **configurationKwargs):
        logger.info(f'{__class__.__name__}.basic')
        TravisExecutor(**configurationKwargs).task(Travis.TASK_MODE_BASIC, *secrets)
        GitExecutor(**configurationKwargs).task(Travis.TASK_MODE_BASIC, gitMsg)

    @staticmethod
    def aws(gitMsg: str = None, *secrets: str, **configurationKwargs):
        logger.info(f'{__class__.__name__}.aws')
        TravisExecutor(**configurationKwargs).task(Travis.TASK_MODE_AWS, *secrets)
        GitExecutor(**configurationKwargs).task(Travis.TASK_MODE_AWS, gitMsg)

    @staticmethod
    def encrypt(*secrets: str, **configurationKwargs):
        logger.info(f'{__class__.__name__}.encrypt')
        TravisExecutor.encrypt(*secrets, **configurationKwargs)
