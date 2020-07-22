#!/usr/bin/env python3.7
import inspect
import logging


def PrintFrame(depth: int = 1):
    callerframerecord = inspect.stack()[2]  # 0 represents this line, # 1 represents line at caller
    frame : inspect.FrameInfo = callerframerecord[0]
    print(frame, inspect.getlineno(frame))
    return


def loggify(logger: logging.Logger, cls, clb: callable, ):
    def wrapper(*args, **kwargs):
        # PrintFrame(depth=4)
        logger.info(f'{cls.__name__}.{clb.__name__}')
        logger.debug(f'ARGS {args}')
        logger.debug(f'KWARGS {kwargs}')
        return clb(*args, **kwargs)
    wrapper.__name__ = clb.__name__
    return wrapper


def logify_class(logName: str):
    def decorate(cls):
        decorate.__name__ = cls.__name__
        cls.logger = logging.getLogger(logName)
        for attrName, attr in inspect.getmembers(cls):
            if inspect.ismethod(attr):
                if inspect.isclass(attr):
                    print(f'CLASS : {attr.__class__.__name__}.{attrName}.{attr.__class__}.{attr.__name__} ')
                else:
                    setattr(cls, attrName, loggify(cls.logger, cls, attr, ))
            elif inspect.isfunction(attr):
                setattr(cls, attrName, loggify(cls.logger, cls, attr, ))
        return cls
    return decorate
