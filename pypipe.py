#!/usr/bin/env python3

import sys
import os
import pty
import tty
import select
import subprocess

STDIN_FILENO = 0
STDOUT_FILENO = 1
STDERR_FILENO = 2

def _writen(fd, data):
    while data:
        n = os.write(fd, data)
        data = data[n:]

def main_loop(master_fd, extra_input):
    fds = [master_fd, STDIN_FILENO]

    _writen(master_fd, extra_input)

    while True:
        rfds, _, _ = select.select(fds, [], [])
        if master_fd in rfds:
            data = os.read(master_fd, 1024)
            if not data:
                fds.remove(master_fd)
            else:
                os.write(STDOUT_FILENO, data)
        if STDIN_FILENO in rfds:
            data = os.read(STDIN_FILENO, 1024)
            if not data:
                fds.remove(STDIN_FILENO)
            else:
                _writen(master_fd, data)

def main():
    extra_input = sys.argv[1]
    interactive_command = sys.argv[2]

    if hasattr(os, "fsencode"):
        # convert them back to bytes
        # http://bugs.python.org/issue8776
        interactive_command = os.fsencode(interactive_command)
        extra_input = os.fsencode(extra_input)

    # add implicit newline
    if extra_input and extra_input[-1] != b'\n':
        extra_input += b'\n'

    # replace LF with CR (shells like CR for some reason)
    extra_input = extra_input.replace(b'\n', b'\r')

    pid, master_fd = pty.fork()

    if pid == 0:
        os.execlp("sh", "/bin/sh", "-c", interactive_command)

    try:
        mode = tty.tcgetattr(STDIN_FILENO)
        tty.setraw(STDIN_FILENO)
        restore = True
    except tty.error:    # This is the same as termios.error
        restore = False

    try:
        main_loop(master_fd, extra_input)
    except OSError:
        if restore:
            tty.tcsetattr(0, tty.TCSAFLUSH, mode)

    os.close(master_fd)
    return os.waitpid(pid, 0)[1]

if __name__ == "__main__":
    main()
