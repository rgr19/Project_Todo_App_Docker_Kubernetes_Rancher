#!/usr/bin/env python3.7

from handlers.lib.TaskHandler import TaskHandler


class Kompose:
    class Prod(TaskHandler):

        def __call__(self, parser, namespace, values, option_string=None):
            print('[CALL][DOCKER PROD RUN] %r => VALUES: %r => OPTION_STRING: %r' % (namespace, values, option_string))
            setattr(namespace, self.dest, self.const)

    class Dev(TaskHandler):

        def __call__(self, parser, namespace, values, option_string=None):
            print('[CALL][DOCKER DEV RUN] %r => VALUES: %r => OPTION_STRING: %r' % (namespace, values, option_string))
            setattr(namespace, self.dest, self.const)
