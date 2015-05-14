
import errno
import os


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

BASEPATH = '/tmp/pyPaaS'
mkdir_p(BASEPATH)

PATH_SUFFIX = '/fintura/pyPaaS/venv/bin'
