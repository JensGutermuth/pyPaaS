#!/usr/bin/env python
# -*- coding: utf-8 -*-

import errno
import os
import os.path


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def replace_file(filename, new_contents, chmod=None):
    """
    Leaves either the old file, the old file and a .new file or the new file.

    Writes to .new, calls fsync and then renames to the original filename.
    """
    with open(filename + '.new', 'w') as newf:
        newf.write(new_contents)
        newf.flush()
        if chmod is not None:
            os.chmod(filename + '.new', chmod)
        os.fsync(newf.fileno())
    os.rename(filename + '.new', filename)
