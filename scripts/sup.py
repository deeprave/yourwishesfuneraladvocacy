#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-function dot.env utility script
"""
import sys
import argparse
import re
from string import Template
from typing import Union
from pathlib import Path
from django_env.dot_env import load_env


def read_env(envfile: Union[str, Path], search=None, parents=False, useenv=False):
    """Read the entire .env file"""
    if search is None:
        search_path = [Path.cwd()]
    else:
        search_path = set()
        for path in [p.split(',') for p in search]:
            for p in path:
                search_path.add(Path(p).resolve(strict=True))
        search_path = list(search_path)
    environ = None if useenv else {}
    return load_env(envfile, search_path=search_path, parents=parents, update=False, environ=environ)


def cache_regex(rx: str) -> re.Pattern:
    if not hasattr(cache_regex, 'cache'):
        cache_regex.cache = {}
    cache = cache_regex.cache
    if rx not in cache:
        cache[rx] = re.compile(rx)
    return cache[rx]


def env_command(args: argparse.Namespace):
    if args.env_command:
        env = read_env(args.dotenv, search=args.search, parents=args.parents, useenv=args.environ)
        regex_list = args.regex
        is_value = args.env_command == 'value'
        if is_value:
            # other than only a single regex whcih is actually just a string it is almost the same as list -a
            args.values, args.vars = True, False
        elif not (args.values or args.vars):
            args.values, args.vars = True, True

        def match(var, regexlist):
            if regexlist:
                for regex in regexlist:
                    if is_value:
                        if var == regex:
                            break
                    elif cache_regex(regex).match(var):
                        break
                else:
                    return False
            return True

        def fmt(var, val):
            return f"{var}={val}" if all((args.values, args.vars)) else f"{var}" if args.vars else f"{val}"

        def output(string):
            print(string)

        for variable, value in env.items():
            if match(variable, regex_list):
                output(fmt(variable, value))
                if is_value:
                    break


def subst(environ, lines) -> list:
    """ post-process the variables using ${substitutions} """
    def do_subst(value: str) -> str:
        if all(v in value for v in ('${', '}')):  # looks like template
            # ignore anything that does not resolve, don't throw an exception!
            value = Template(value).safe_substitute(environ)
        return value

    for line in lines:
        if isinstance(line, tuple):
            var, val = line[0], do_subst(line[1])
            environ[var] = val      # update the environment
            yield f"{var}={val}"    # and yield key=value pair
        else:
            yield line              # yield the literal line


def parse_template(env, template):

    with open(template, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                yield line
            else:
                parts = line.split('=', maxsplit=1)
                if len(parts) == 1:
                    var = parts[0]
                    val = env.get(parts[0], '')
                else:
                    var = parts[0], parts[1]
                yield var, val


def output_result(lines, outputfile):

    def writelines(fp, _lines):
        linecount = 0
        for linecount, line in enumerate(_lines):
            print(line, file=fp)
        print(f"{outputfile}: {linecount+1} line(s) written", file=sys.stderr)

    if outputfile == '-':
        writelines(sys.stdout, lines)
    else:
        with open(outputfile, 'w+') as f:
            writelines(f, lines)


def build_command(args):
    env = read_env(args.dotenv, search=args.search, parents=args.parents, useenv=args.environ)
    data = parse_template(env, args.template)
    rendered = subst(env, data)
    output_result(rendered, args.output)


def realpath_command(args):
    relative = Path(args.relative_to).resolve(strict=True) if args.relative_to else None
    for path in args.paths:
        path = Path(path).resolve(strict=True)
        if not path.is_dir():
            path = path.parent
        try:
            print(path.relative_to(relative) if relative else path)
        except ValueError:
            print(path)


def error(message, exitcode=None):
    print(message, file=sys.stderr)
    if exitcode is not None:
        exit(exitcode)


if __name__ == '__main__':

    prog = Path(sys.argv[0]).resolve(strict=True)
    parser = argparse.ArgumentParser(prog=prog.name, description=__doc__)

    cwd = Path().cwd().resolve(strict=True)
    scripts = prog.parent.relative_to(cwd)
    dotenv_default = '.env'
    template_default = scripts / 'env-template'
    output_default = 'docker.env'

    parser.add_argument('-e', '--environ', action='store_true', default=False,
                        help='add OS environment to the list')
    parser.add_argument('-d', '--dotenv', action='store', default=dotenv_default,
                        help=f'name of dot.env file (default={dotenv_default})')
    parser.add_argument('-s', '--search', action='store', nargs='?',
                        help='search path for env file (comma separated)')
    parser.add_argument('-p', '--parents', action='store_true', default=False,
                        help='search parents until a dotenv file is found')

    subparsers = parser.add_subparsers(dest='command')

    # env
    env_parser = subparsers.add_parser('env', help='.env functions')

    env_subparsers = env_parser.add_subparsers(title='env', dest='env_command')
    # env list
    list_parser = env_subparsers.add_parser('list', help='list env variables, values or both')
    list_group = list_parser.add_mutually_exclusive_group()
    list_group.add_argument('-a', '--values', action='store_true', default=False,
                            help='list values only')
    list_group.add_argument('-v', '--vars', action='store_true', default=False,
                            help='list variables only')
    list_parser.add_argument('regex', action='store', nargs='*',
                             help='select variables by regular expression')

    # env value
    value_parser = env_subparsers.add_parser('value', help='list env variables, values or both')
    value_parser.add_argument('regex', action='store', nargs=1,
                              help='select variable(s) by regular expression')

    # build
    build_parser = subparsers.add_parser('build', help='build env list from template')

    build_parser.add_argument('-t', '--template', action='store', default=template_default,
                              help=f'template file to use to use (default="{template_default}")')
    build_parser.add_argument('output', action='store', default=output_default,
                              help=f'output to this file (default="{output_default}")')

    # realpath
    real_parser = subparsers.add_parser('realpath', help='get real (or relative) paths to targets')

    real_parser.add_argument('-r', '--relative_to', action='store', default=None,
                             help='return paths relative to a start path')
    real_parser.add_argument('-d', '--dir', action='store_true', default=False,
                             help='return directory for provided files')
    real_parser.add_argument('paths', action='store', nargs='+',
                             help='resolve real or relative paths')

    argv = parser.parse_args()
    # print(argv)

    commands = {
        'env': env_command,
        'build': build_command,
        'realpath': realpath_command,
    }
    try:
        commands[argv.command](argv)
    except KeyError:
        if not argv.command:
            parser.print_usage(file=sys.stderr)
        else:  # famous last words: should not happen
            error(f'{prog}: uknown command: {argv.command}', exitcode=2)
