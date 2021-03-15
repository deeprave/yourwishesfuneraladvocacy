#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wagtail project setup utility
"""
import os
from subprocess import check_call, CalledProcessError
from shutil import which
import sys
import json
import secrets
from collections import defaultdict
from datetime import datetime
from string import Template
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Union, TextIO, Any

exists = os.path.exists

DOTENV = '.env'
DOTENVTEMPLATE = '.env-template'


class OutputTo:
    def __init__(self, destination: Union[None, TextIO, str, bytes, Path] = None):
        self.output_to = destination or sys.stdout
        self.require_close = destination not in (sys.stdout, sys.stderr)

    def __enter__(self):
        if isinstance(self.output_to, (str, Path)):
            self.output_to = open(self.output_to, 'w')
            self.require_close = True
        return self.output_to

    def __exit__(self, _type, value, traceback):
        if self.require_close:
            self.output_to.close()


class MessageLog:
    DEFAULT_PREFIX = '-'

    def __init__(self, fp=None, prefix=DEFAULT_PREFIX):
        self._fp = fp or sys.stdout
        self._console = fp in (sys.stderr, sys.stdout)
        self.prefix = prefix
        self._messages = []

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self, prefix):
        self._prefix = f'{prefix} ' if prefix else ''

    def _add(self, msgs: Union[list, str] = None):
        if isinstance(msgs, (list, tuple)):
            self._messages.extend(msgs)
        elif msgs:
            self._messages.append(msgs)

    def flush(self, prefix=None):
        if self._messages:
            prefix = prefix if prefix else self._prefix
            with OutputTo(self._fp) as f:
                for message in self._messages:
                    print(f'{prefix}{message}', file=f)
            self._messages = []

    def info(self, msgs: Union[list, str] = None, cache: bool = False) -> None:
        self._add(msgs)
        if not cache:
            self.flush()

    def error(self, msgs: Union[list, str] = None) -> None:
        self.flush()
        self._add(msgs)
        self.flush(prefix=f'!{self._prefix}')


class EnvManager:

    DEFAULTS = {
        'docker': {
            'COMPOSE_PROJECT_NAME': 'myapp',
            'COMPOSE_FILE': 'docker-compose.yml',
        },
        'app': {
            'APP_NAME': '',
            'APP_DIR': '',
            'APP_ROOT': '',
            'APP_PORT': 8000,
        },
        'django': {
            'DJANGO_SECRET_KEY': None,
            'DJANGO_MODE': 'dev',
            'DJANGO_USER': 'crm',
            'DJANGO_BASE_URL': 'https://example.com'
        },
        'database': {
            'DBHOST': '127.0.0.1',
            'DBPORT': 5432,
            'DBROLE': '',
            'DBNAME': '',
            'DBUSER': '',
            'DBPASS': '',
            'POSTGRES_PASSWORD': '',
            'DATABASE_URL': 'postgres://${DBUSER}:${DBPASS}@${DBHOST}:${DBPORT}/${DBNAME}'
        },
        'redis': {
            'RDHOST': 'redis',
            'RDPORT': 6379,
            'RDB': 0,
            'CACHE_URL': 'redis://${RDHOST}:${RDPORT}/${RDB}',
        },
        'email': {
            'EMAIL_HOST_USER': 'user@example.com',
            'EMAIL_HOST_PASSWORD': '',
            'EMAIL_HOST': 'smtp.gmail.com',
            'EMAIL_PORT': 587,
            'EMAIL_URL': 'smtp+tls://${EMAIL_HOST_USER}:${EMAIL_HOST_PASSWORD}@${EMAIL_HOST}:${EMAIL_PORT}/',
        },
        'ext': {
            'EXT_ROOT': '${APP_DIR}',
            'EXT_STATIC': '${APP_DIR}/static',
            'EXT_MEDIA': '${APP_DIR}/media',
        },
        'storage': {
            'S3_DOMAIN': '',
            'S3_REGION': '',
            'S3_ACCESS_KEY': '',
            'S3_SECRET_KEY': '',
            'S3_BUCKET_NAME': '',
            'S3_BUCKET_POLICY': '',
        },
        'stripe': {
            'STRIPE_PUBLIC_KEY': '',
            'STRIPE_PRIVATE_KEY': '',
            'STRIPE_SIGNING_KEY': '',
        },
        'sentry': {
            'SENTRY_DSN': "https://02681a846266431889b46a7515f035c7@o440352.ingest.sentry.io/5409078",
        },
    }

    def __init__(self, env_file: Union[str, Path]):
        self._env = {}
        for section, vardict in self.DEFAULTS.items():
            if isinstance(vardict, dict):
                for var, val in vardict.items():
                    self._env.setdefault(var, self.quote(val))
            else:
                self._env.setdefault(section, self.quote(vardict))
        self.datestamp = True
        self.docker = False
        self.volumes = False
        self.force = False
        self._messages = MessageLog()
        self.messages.info(f'initialising environment from {env_file}')
        self.parse_env(env_file)

    @classmethod
    def default(cls, var) -> Any:
        return cls.DEFAULTS.get(var)

    @staticmethod
    def unquote(line):
        if line[0] in '"\'' and line[-1] == line[0]:
            line = line[1:-1]
        return line

    @staticmethod
    def quote(line):
        if any([c in line for c in "~!@#$%^&*()-+=?<>,/"]):
            line = f'"{line}"'
        return line

    def parse_env(self, env_file: str) -> None:
        current = {}
        with open(env_file, 'r') as f:
            for index, line in enumerate(f):

                def error(message):
                    self.messages.info(f"{env_file}({index + 1}): {message}")

                line = line.strip()
                # skip empty and comments
                if line and line[0] != '#':
                    s = line.split('=', 1)
                    if len(s) != 2:
                        error('malformed line')
                    else:
                        var, val = s
                        if var in current:
                            error(f'multiple definitions of {var}, overridden')
                        current[var] = self.unquote(val)
        self._env.update(current)

    @property
    def env(self) -> dict:
        return self._env

    @property
    def messages(self) -> MessageLog:
        return self._messages

    def getvar(self, var: str) -> Any:
        return self._env.get(var)

    def getvars(self, *args: [str]) -> [Any]:
        return tuple([self.getvar(arg) for arg in args])

    def setvar(self, var: str, val: Any) -> None:
        if val is None:
            if var in self._env:
                del self._env[var]
        else:
            self.env[var] = str(val)

    def defines(self, value):
        if value:
            if isinstance(value, (list, tuple)):
                for val in value:
                    self.defines(val)
            else:
                values = value.split(',')
                if len(values) > 1:
                    self.defines(values)
                else:
                    s = values[0].split('=', 1)
                    if len(s) < 2:
                        self.messages.info(f"invalid define: {values[0]}")
                    else:
                        self.setvar(s[0], self.unquote(s[1]))

    P_CHRS = '!#$%&{}*+-.0123456789:;?@ABCDEFGHIJKLMNOPQRSTUVWXYZ^_`abcdefghijklmnopqrstyvwxyz{}'

    @classmethod
    def gen_secret_key(cls):
        # multiple of 3 for base64 to avoid = fillers
        return secrets.token_urlsafe(51)

    @classmethod
    def gen_password(cls):
        return secrets.token_urlsafe(18)

    def apply(self, args: Namespace):
        self.messages.info('adjusting options from commandline')
        self.docker = args.docker
        self.volumes = args.volumes
        self.force = args.force
        self.defines(args.define)

        if self.docker:
            self.setvar('COMPOSE_FILE', 'docker-compose-services.yml:docker-compose.yml')
        else:
            self.setvar('COMPOSE_FILE', 'docker-compose.yml')

        if args.project:
            self.setvar('COMPOSE_PROJECT_NAME', args.project)

        if args.app:
            self.setvar('APP_NAME', args.app)

        app_name = self.getvar('APP_NAME')

        if args.directory:
            self.setvar('APP_DIR', args.directory)
        elif not self.getvar('APP_DIR'):
            self.setvar('APP_DIR', app_name)

        if args.srvroot or not self.getvar('APP_ROOT'):
            self.setvar('APP_ROOT', args.srvroot or '/srv')

        if args.url:
            self.setvar('BASE_URL', args.url)
        elif not self.getvar('BASE_URL'):
            self.setvar('BASE_URL', 'https://example.com')

        if args.secret or not self.getvar('DJANGO_SECRET_KEY'):
            self.setvar('DJANGO_SECRET_KEY', self.gen_secret_key())

        if args.mode or not self.getvar('DJANGO_MODE'):
            self.setvar('DJANGO_MODE', args.mode or 'dev')

        if args.dbhost or not self.getvar('DBHOST'):
            self.setvar('DBHOST', args.dbhost or 'localhost')

        if args.rdhost or not self.getvar('RDHOST'):
            self.setvar('RDHOST', args.rdhost or 'localhost')

        if args.dbname or not self.getvar('DBNAME'):
            self.setvar('DBNAME', args.dbname or app_name)

        if args.dbrole or not self.getvar('DBROLE'):
            self.setvar('DBROLE', args.dbrole or app_name)

        if args.dbuser or not self.getvar('DBUSER'):
            self.setvar('DBUSER', args.dbuser or f'{app_name}_user')

        if args.dbpass:
            self.setvar('DBPASS', args.dbpass)
        elif args.randdb or not self.getvar('DBPASS'):
            self.setvar('DBPASS', self.gen_password())

        if args.sapass:
            self.setvar('POSTGRES_PASSWORD', args.sapass)
        elif args.randsa or not self.getvar('POSTGRES_PASSWORD'):
            self.setvar('POSTGRES_PASSWORD', self.gen_password())

        if args.prefix:
            self.setvar('RDPORT', str(args.prefix) + '6379')
            self.setvar('DBPORT', str(args.prefix) + '5432')
        else:
            if args.dbport or not self.getvar('DBPORT'):
                self.setvar('DBPORT', args.dbport or '5432')

            if args.rdport or not self.getvar('RDPORT'):
                self.setvar('RDPORT', args.rdport or '6379')

        if args.cache or not self.getvar('RDB'):
            self.setvar('RDB', args.cache or 0)

        if self.volumes:
            if not self.getvar('EXT_ROOT'):
                self.setvar('EXT_ROOT', self.getvar('APP_ROOT'))
            if not self.getvar('EXT_STATIC'):
                self.setvar('EXT_STATIC', 'data-static')
            if not self.getvar('EXT_MEDIA'):
                self.setvar('EXT_MEDIA', 'data-media')
        else:
            cwd = os.getcwd()
            if not self.getvar('EXT_ROOT'):
                self.setvar('EXT_ROOT', cwd)
            if not self.getvar('EXT_STATIC'):
                self.setvar('EXT_STATIC', os.path.join(cwd, 'static'))
            if not self.getvar('EXT_MEDIA'):
                self.setvar('EXT_MEDIA', os.path.join(cwd, 'media'))

    def resolve(self) -> dict:
        self.messages.info('resolving variables')
        env = self.env.copy()
        for k, v in self.env.items():
            if '$' in v:
                v = Template(v).safe_substitute(env)
            env[k] = v
        return env

    def dump(self, destination: Union[None, str, bytes, Path] = None, env: dict = None) -> None:
        with OutputTo(destination) as f:
            json.dump(self.env if env is None else env, f, indent=2)

    def render(self, destination: Union[None, str, bytes, Path] = DOTENV, env: dict = None) -> None:
        if isinstance(destination, (str, bytes, Path)):
            self.messages.info(f'rendering env to {destination}')

        with OutputTo(destination) as f:
            if self.datestamp:
                print(f'# generated {datetime.now().isoformat()}', file=f)
            self.messages.prefix = None
            self.messages.info('┌────')
            self.messages.prefix = '|'

            section_mappings = {
                'django': 'django',
                'email': 'email',
                'ext': 'ext',
                'db': 'database',
                'rd': 'cace',
                'mc': 'cache',
                'database': 'database',
                's3': 'storage',
                'stripe': 'stripe',
                'sentry': 'sentry'
            }

            def key_to_section(key):
                try:
                    return section_mappings[key.lower()]
                except KeyError:
                    pass
                return None

            sectionref = {}
            for section, vardict in self.DEFAULTS.items():
                if isinstance(vardict, dict):
                    for var, val in vardict.items():
                        sectionref[var] = section
                else:
                    sectionref[vardict] = key_to_section(vardict)

            rendered = defaultdict(dict)
            for key, value in env.items():
                section = sectionref.get(key, None)
                rendered[section][key] = value

            for section, keys in rendered.items():
                print(f"\n# {section}" if section else "\n#", file=f)

                for key, value in keys.items():
                    what = f'{key}={self.quote(value)}'
                    print(what, file=f)
                    if f not in (sys.stdout, sys.stderr):
                        self.messages.info(what, cache=True)

            self.messages.flush()
            self.messages.prefix = None
            self.messages.info('└────')


def install_dependancies(_: EnvManager):
    messages = MessageLog(prefix='+')

    def pip_install():
        messages.info(f'Updating pip')
        yield 'pip', [sys.executable, '-m', 'pip', 'install', '-qU', 'pip', 'setuptools', 'wheel']
        for requirements in ('requirements-dev.txt', 'requirements.txt'):
            if exists(requirements):
                yield 'pip', [sys.executable, '-m', 'pip', 'install', '-qr', requirements]

    def pipenv_install():
        pipenv = which('pipenv')
        if pipenv is None:
            ValueError('pipenv is not installed but is required for this installation')
        os.environ['PIPENV_VENV_IN_PROJECT'] = '1'
        yield 'pipenv', [pipenv, 'install']

    def poetry_install():
        poetry = which('poetry')
        if poetry is None:
            ValueError('poetru is not installed but is required for this installation')
        yield 'poetry', [poetry, 'install']

    # select installer, default to pip
    installer = pip_install
    if exists('Pipfile'):
        installer = pipenv_install
    elif exists('pyproject.toml'):
        installer = poetry_install

    try:
        for method, args in installer():
            try:
                messages.info(f'Installing python dependencies ({method})')
                check_call(args)
                messages.info('Done')
            except CalledProcessError as cpe:
                messages.error(f'{method} failure: error {cpe.returncode}: {cpe.output}')
                return False
    except ValueError:
        # early installer errors
        return False
    return True


def wagtail_deployment(env: EnvManager):
    messages = MessageLog(prefix='>')

    app_dir, app_name = env.getvars('APP_DIR', 'APP_NAME')
    messages.info(f'Creating wagtail project "{app_name}" in dir "{app_dir}"')
    try:
        if exists(app_dir):
            messages.error(f'wagtail project creation skipped - dir "{app_dir}" already exists')
        else:
            os.mkdir(app_dir)
            check_call(['wagtail', 'start', app_name, app_dir])

        # remove these distractions
        removelist = env.getvar('PURGE').split(',')
        if removelist:
            for filename in removelist:
                path = os.path.join(app_dir, filename)
                if exists(path):
                    os.remove(path)
        messages.info('Done')
        return True

    except CalledProcessError as cpe:
        messages.error(f'pip failure: error {cpe.returncode}: {cpe.output}')
        return False


def wagtail_settings(env: EnvManager):
    messages = MessageLog(prefix='*')
    messages.info('Adjusting wagtail project')

    app_dir, app_name, base_url, secret_key, django_mode = \
        env.getvars('APP_DIR', 'APP_NAME', 'BASE_URL', 'DJANGO_SECRET_KEY', 'DJANGO_MODE')
    app_root = os.path.join(app_dir, app_name)
    settings_dir = os.path.join(app_root, 'settings')
    settings_module = f'"{app_name}.settings." + os.environ.get("DJANGO_MODE", "dev")'

    def set_file_content(path: str, content: str, executable=False, force=False):
        if exists(path) and not force:
            messages.error(f'module {path} skipped, already exists')
        else:
            messages.info(f'creating {path}')
            with open(path, 'w') as fp:
                fp.write(content)
        if executable:
            os.chmod(path, 0o755)

    try:
        set_file_content(os.path.join(app_dir, 'pytest.ini'), f"""[pytest]
DJANGO_SETTINGS_MODULE = {app_name}.settings.{django_mode}
""", force=True)

        set_file_content(os.path.join(app_dir, 'manage.py'), f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", {settings_module})

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
""", executable=True, force=True)

        set_file_content(os.path.join(app_root, 'wsgi.py'), f"""# -*- coding: utf-8 -*-
# WSGI config for {app_name} project
import os

from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", {settings_module})

application = get_wsgi_application()
""", force=True)

        set_file_content(os.path.join(app_root, 'asgi.py'), f"""# -*- coding: utf-8 -*-
# ASGI config for {app_name} project
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", {settings_module})

application = get_asgi_application()
""", force=True)

        set_file_content(os.path.join(settings_dir, 'local.py'), f"""# -*- coding: utf-8 -*-
import django_env
env = Env()
if env.bool('DJANGO_READ_DOT_ENV_FILE', False):
    env.read_env(search_path=Path.cwd(), parents=True) 

# ImproperlyConfigured if not set
SECRET_KEY = env.get('DJANGO_SECRET_KEY')

# Override defaults

CACHES = {{
    "default": env.cache_url(default='redis://localhost:6329/0') 
}}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

DATABASES = {{
    "default": env.database_url(default=f'sqlite://{{BASE_PATH / 'db.sqlite3'}}'),
}}

WAGTAIL_SITE_NAME = '{app_name}'
BASE_URL = env.get('DJANGO_BASE_URL', '{base_url}')

""")

        set_file_content(os.path.join(settings_dir, 'secrets.py'), f"""# -*- coding: utf-8 -*-
SECRET_KEY = '{secret_key}'
""", force=True)

        set_file_content(os.path.join(settings_dir, '.gitignore'), "secrets.py\n", force=True)

        messages.info('Done')

    except BaseException as exc:
        messages.error(f'{exc}: {exc.args}')
        return False

    return True


if __name__ == '__main__':

    prog = os.path.basename(sys.argv[0])
    parser = ArgumentParser(prog=prog, description=__doc__)

    envfile = DOTENV if exists(DOTENV) else DOTENVTEMPLATE

    e = EnvManager(os.getenv('ENV') or envfile)

    def d(var: str):
        value = e.getvar(var)
        return '' if value is None else f"({value})"

    parser.add_argument('--project', '-X',                      help=f"set project name {d('COMPOSE_PROJECT_NAME')}")
    parser.add_argument('--app', '-a',                          help=f"set app name {d('APP_NAME')}")
    parser.add_argument('--directory', '-d',                    help='set app directory (same as app name)')
    parser.add_argument('--srvroot', '-x',                      help='absolute root path for deployment')
    parser.add_argument('--novirtualenv', '-N',                 help='ignore virtualenv presence check')
    parser.add_argument('--url', '-U',                          help=f"set site base url {d('BASE_URL')}")
    parser.add_argument('--force', '-f', action='store_true',   help='force wagtail project create')
    parser.add_argument('--docker', '-S', action='store_true',  help=f"assume docker services")
    parser.add_argument('--volumes', '-v', action='store_true', help='use data volumes for app')
    parser.add_argument('--randdb', '-r', action='store_true',  help='generate new random db user password')
    parser.add_argument('--randsa', '-R', action='store_true',  help='generate new random db sa password')
    parser.add_argument('--secret', '-K', action='store_true',  help='generate random SECRET_KEY')
    parser.add_argument('--define', '-D', action='append', nargs='?', help='define one or more arguments')
    parser.add_argument('--mode', '-m', choices=('dev', 'beta', 'production', 'test'),
                        help='select django environment')
    parser.add_argument('--prefix', '-E', type=int, choices=range(1, 7),
                        help='set an offset for std pg,redis ports')

    postgres = parser.add_argument_group(title='PostgreSQL', description='database options')
    postgres.add_argument('--dbhost', '-i',                     help='database hostname (prefer IP)')
    postgres.add_argument('--dbport', '-p', type=int,           help='database port')
    postgres.add_argument('--dbname', '-n',                     help='database or schema name')
    postgres.add_argument('--dbrole', '-g',                     help='database role or owner')
    postgres.add_argument('--dbuser', '-u',                     help='database username')
    postgres.add_argument('--dbpass', '-w',                     help='database password')
    postgres.add_argument('--sapass', '-G',                     help='database administrator password')

    redis = parser.add_argument_group(title='Redis', description='cache options')
    redis.add_argument('--rdhost', '-I',                        help='redis hostname (prefer IP)')
    redis.add_argument('--rdport', '-P', type=int,              help='redis port')
    redis.add_argument('--rdb',    '-c', type=int, choices=range(0, 16),   help='redis db # (0-15)')

    parser.add_argument('command', nargs='*',                   help='(optional) command')

    argv = parser.parse_args()

    e.apply(argv)

    e.messages.flush()

    if argv.command:
        for command in argv.command:
            if command == 'dump':
                e.dump(env=e.resolve())
    else:
        e.render(env=e.resolve())

    virtual_env = os.getenv('VIRTUAL_ENV')
    if not virtual_env and not argv.novirtualenv:
        print('No virtual-env active (nor overridden)')
    else:
        print(f'Using virtual-env {os.path.basename(virtual_env)} [from {virtual_env}]')
        if install_dependancies(e):
            if wagtail_deployment(e):
                if wagtail_settings(e):
                    if e.docker:
                        check_call(['docker-compose', '-f', 'docker-compose-services.yml', 'up', '-d'])
