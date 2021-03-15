#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os

relpath, realpath = os.path.relpath, os.path.realpath

def realpaths(paths, *, relative=None):

    relative = realpath(relative) if relative else None
    for path in paths:
        path = realpath(path)
        print(relpath(path, relative) if relative else path)


if __name__ == '__main__':
    relative_to = None

    argv, skip = [], True
    for index, arg in enumerate(sys.argv):
        if skip:
            skip = False
        elif arg.startswith('-'):
            for pfx in ('-r', '--relative-to'):
                if arg.startswith(pfx):
                    pfx_len = len(pfx)
                    if len(arg) > pfx_len and arg[pfx_len] == '=':
                        relative_to = arg[pfx_len+1:]
                    else:
                        try:
                            relative_to = sys.argv[index+1]
                            skip = True
                        except IndexError as exc:
                            raise IndexError(f'{pfx} requires and argument') from exc
                    break
            else:
                raise ValueError(f'unknown option {arg}')
        else:
            argv.append(arg)
    realpaths(argv, relative=relative_to)
