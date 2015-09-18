import sys
from contextlib import contextmanager

_section_stack = []


def print_header(msg, level=0, file=sys.stdout, flush=False):
    try:
        char = '#=-.'[level]
    except IndexError:
        raise RuntimeError('only header levels >= 0 and < 3 are supported')
    print(char*70, file=file)
    print('{0}\n{0}  {1}\n{0}'.format(char*2, msg), file=file)
    print(char*70 + '\n', file=file, flush=flush)


def print_message(msg, level=0, file=sys.stdout, flush=False):
    try:
        char = '#=-.'[level]
    except IndexError:
        raise RuntimeError('only header levels >= 0 and < 3 are supported')
    print('{0}  {1}'.format(char*2, msg), file=file)


@contextmanager
def logging_section(name):
    global _section_stack
    _section_stack.append(name)
    try:
        print_header(
            msg=" → ".join(_section_stack),
            level=len(_section_stack) - 1,
            file=sys.stderr,
            flush=True)

        yield

        print('', file=sys.stderr)  # prints a newline
        print_message(
            msg=" > ".join(_section_stack) + ' done\n',
            file=sys.stderr,
            level=len(_section_stack) - 1,
            flush=True)
    finally:
        _section_stack.pop()
