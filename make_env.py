#!/usr/bin/env python3
"""
Build a .env file based on a template - renders a .env for use within a container
without including unneeded vars used in development
"""
import os
import sys
from pathlib import Path
import argparse
from string import Template
from typing import Sequence

from django_env import Env


def subst(environ: Env, lines: Sequence) -> list:
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


def parse_template(env: Env, template: Path) -> Sequence:

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


def output_result(lines: list, outputfile: Path):

    def writelines(fp, lines):
        linecount = 0
        for linecount, line in enumerate(lines):
            print(line, file=fp)
        print(f"{outputfile}: {linecount+1} line(s) written", file=sys.stderr)

    if outputfile == '-':
        writelines(sys.stdout, lines)
    else:
        with open(outputfile, 'w+') as f:
            writelines(f, lines)


if __name__ == '__main__':

    prog = Path(__file__).resolve(strict=True)
    parser = argparse.ArgumentParser(prog=prog.name, description=__doc__)
    dotenv_default = '.env'
    template_default = 'env-template'
    output_default = 'docker.env'
    parser.add_argument('-e', '--envfile', action='store', default=dotenv_default,
                        help=f'source values to render from this file (default="{dotenv_default}")')
    parser.add_argument('-t', '--template', action='store', default=template_default,
                        help=f'template file to use to use (default="{template_default}"')
    parser.add_argument('-n', '--noenv', action='store_true', default=False,
                        help='prevent loading current os.environ values (default=False)')
    parser.add_argument('output', action='store', default=output_default,
                        help=f'output to this file (default="{output_default}")')
    args = parser.parse_args()

    template = Path(args.template).resolve(strict=True)
    envfile = Path(args.envfile).resolve(strict=True)
    environ = args.noenv if args.noenv else os.environ

    env = Env(readenv=True, env_file=args.envfile, environ=environ, search_path=envfile.parent)

    data = parse_template(env, args.template)
    rendered = subst(env, data)
    output_result(rendered, args.output)
