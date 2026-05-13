import os
import sys
from contextlib import contextmanager


@contextmanager
def suppress_native_output(enabled: bool = True):
    """
    Silencia stdout/stderr a nivel de file descriptor.

    Útil para librerías nativas como llama.cpp que escriben directamente
    en C stdout/stderr y no respetan siempre verbose=False.
    """
    if not enabled:
        yield
        return

    stdout_fd = sys.stdout.fileno()
    stderr_fd = sys.stderr.fileno()

    saved_stdout_fd = os.dup(stdout_fd)
    saved_stderr_fd = os.dup(stderr_fd)

    try:
        with open(os.devnull, "w") as devnull:
            os.dup2(devnull.fileno(), stdout_fd)
            os.dup2(devnull.fileno(), stderr_fd)
            yield
    finally:
        os.dup2(saved_stdout_fd, stdout_fd)
        os.dup2(saved_stderr_fd, stderr_fd)

        os.close(saved_stdout_fd)
        os.close(saved_stderr_fd)