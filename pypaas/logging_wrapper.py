import os
import shlex
import subprocess
import sys
import time
from threading import Thread

from queue import Queue

from .options import main


def logging_wrapper():
    """
    Wraps the a process and copies it's log output to a logger process.

    The logger process is specified in the normal pypaas main configuration
    file as "deploy_logger_cmd".

    If "deploy_logger_cmd" is not defined, 'cat > /dev/null' is used.
    """
    def relay(name, src, dsts):
        def real_relay():
            while True:
                s = src.read(1)
                if len(s) == 0:
                    break
                for idx, d in enumerate(dsts):
                    try:
                        d.write(s)
                        d.flush()
                    except BrokenPipeError:
                        # Happens if a logger dies prematurely
                        pass
        return real_relay

    logger = subprocess.Popen(
        main.get('deploy_logger_cmd', 'cat > /dev/null'),
        shell=True,
        stdin=subprocess.PIPE,
    )
    wrapped = subprocess.Popen(
        sys.argv[1:],
        stderr=subprocess.STDOUT,
        stdout=subprocess.PIPE,
    )

    b_stderr = os.fdopen(sys.stderr.fileno(), "wb", 0)
    b_stdout = os.fdopen(sys.stdout.fileno(), "wb", 0)

    wrapped_stdout_relay = Thread(
        target=relay(
            "wrapped_stdout_relay",
            wrapped.stdout,
            # open stderr in binary mode
            [b_stdout, logger.stdin]
        ),
    )
    wrapped_stdout_relay.start()

    #  Wait for wrapped process to finish
    returncode = wrapped.wait()

    wrapped_stdout_relay.join()

    logger_died = logger.poll() is not None
    if logger_died:
        print("logger died prematurely")

    # With all output from the wrapped process fetched, let's close stdin of
    # the logger process
    logger.stdin.close()
    # and wait for it to finish
    logger_returncode = logger.wait()

    if returncode == 0 and logger_returncode != 0:
        sys.exit(logger_returncode)
    elif returncode == 0 and logger_died:
        sys.exit(1)
    else:
        sys.exit(returncode)
