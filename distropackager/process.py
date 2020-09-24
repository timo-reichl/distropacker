
import os
import sys

import subprocess
from contextlib import ContextDecorator


class ProcessContext(ContextDecorator):
    def __init__(self, cmd, run_dir, print_stdout, cache_stdout):
        super().__init__()

        self.cmd = cmd

        self.run_dir = run_dir
        self.previous_dir = None

        self.stdout = list()

        self.cache_stdout = cache_stdout
        self.print_stdout = print_stdout

    def __enter__(self):
        self.previous_dir = os.getcwd()
        os.chdir(self.run_dir)

        return self._run()

    def __exit__(self, *exc):
        os.chdir(self.previous_dir)
        return False

    @classmethod
    def execute(cls, cmd, run_dir, print_stdout=False, cache_stdout=False):
        with cls(cmd, run_dir, print_stdout=print_stdout, cache_stdout=cache_stdout) as pc:
            return pc

    def _run(self):
        process = subprocess.Popen(self.cmd.split(" "), stdout=subprocess.PIPE)

        while process.stdout.readable():
            line = str(process.stdout.readline(), 'utf-8')

            if self.cache_stdout:
                self.stdout.append(line)

            if self.print_stdout:
                sys.stdout.write(line)

            if process.poll() or not line:
                break

        return self
