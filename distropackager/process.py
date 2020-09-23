
import os
import sys

import subprocess
from contextlib import ContextDecorator


class ProcessContext(ContextDecorator):
    def __init__(self, process_cmd, run_dir, print_stdout=False, cache_stdout=False):
        super().__init__()

        self.process_cmd = process_cmd

        self.run_dir = run_dir
        self.previous_dir = None

        self.stdout = list()

        self.cache_stdout = cache_stdout
        self.print_stdout = print_stdout

    def __enter__(self):
        self.previous_dir = os.getcwd()
        os.chdir(self.run_dir)

        return self.run()

    def __exit__(self, *exc):
        os.chdir(self.previous_dir)
        return False

    def run(self):
        process = subprocess.Popen(self.process_cmd.split(" "), stdout=subprocess.PIPE)

        while process.stdout.readable():
            line = str(process.stdout.readline(), 'utf-8')

            if self.cache_stdout:
                self.stdout.append(line)

            if self.print_stdout:
                sys.stdout.write(line)

            if process.poll() or not line:
                break

        return self
