# -*_ coding: utf-8 -*-
__all__ = (
    'LOGGING',
)


def _logging_path(filename):
    import os
    logdir = os.environ.get('DJANGO_LOGDIR', f'{os.getcwd()}/logs')
    path = os.path.expanduser(os.path.expandvars(os.path.join(logdir, filename)))
    os.makedirs(logdir, exist_ok=True)
    with open(path, 'w+') as _:
        pass
    return path


def _mb(val: int):
    return 1024 * 1024 * val


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s.%(msecs)03d] %(levelname)-8s %(message)s (%(name)s:%(lineno)s)",
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
    },
    'handlers': {
        'logfile': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': _logging_path("info.log"),
            'formatter': 'standard',
            'maxBytes': _mb(50),
            'backupCount': 3,
        },
        'debuglog': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': _logging_path("debug.log"),
            'maxBytes': _mb(250),
            'backupCount': 5,
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'level': 'DEBUG',
            'propagate': True,
        },
        '': {
            'handlers': ['console', 'debuglog', 'logfile'],
            'level': 'DEBUG',
        },
    },
}
