import io
import os
import signal
import subprocess
import threading

import time
from collections import namedtuple

TOTAL_NODES = 4

ignore_errors = {
    "<class 'twisted.internet.error.ConnectionRefusedError'>: Connection was refused by other side: 111: Connection refused.",
    "<class 'twisted.internet.error.ConnectionDone'>: Connection was closed cleanly.",
    "<class 'twisted.internet.error.ConnectError'>: An error occurred while connecting: 113: No route to host.",
    "<class 'twisted.internet.error.TimeoutError'>: User timeout caused connection failure."
}

LogEntry = namedtuple('LogEntry', 'full node_id time version sync_state rest')


class IntegrationTest(object):
    def __init__(self, max_running_time_secs):
        self.max_running_time_secs = max_running_time_secs
        self.start_time = time.time()

    @property
    def running_time(self):
        return time.time() - self.start_time

    @staticmethod
    def max_time_error():
        print("******************** MAX RUNNING TIME ERROR")
        os.kill(os.getpid(), signal.SIGABRT)

    @staticmethod
    def successful_test():
        print("******************** SUCCESS!")
        quit(0)

    @staticmethod
    def fail_test():
        print("******************** FAILED!")
        os.kill(os.getpid(), signal.SIGABRT)

    def start(self):
        proc = subprocess.Popen(["./start_net.sh"], stdout=subprocess.PIPE)

        myThread = threading.Timer(self.max_running_time_secs, IntegrationTest.max_time_error)
        myThread.start()

        try:
            for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
                self.process_log_entry(line)
        except Exception as e:
            print(e)
        finally:
            if myThread.is_alive():
                myThread.cancel()
            proc.kill()

    def check_errors(self, entry_raw: str):
        # Detect errors but ignore acceptable ones
        entry_raw = entry_raw.lower()
        if "error" in entry_raw.lower():
            ignore = False
            for e in ignore_errors:
                if e.lower() in entry_raw:
                    ignore = True
                    break
            if not ignore:
                self.fail_test()

    def parse_entry(self, entry_raw: str):
        # FIXME: Improve this
        entry_parts = entry_raw.split('|')
        if len(entry_parts) > 4:
            log_entry = LogEntry(full=entry_raw,
                                 node_id=entry_parts[0],
                                 time=entry_parts[1],
                                 version=entry_parts[2],
                                 sync_state=entry_parts[3],
                                 rest=entry_parts[4])
        else:
            log_entry = LogEntry(full=entry_raw,
                                 node_id=None,
                                 time=None,
                                 version=None,
                                 sync_state=None,
                                 rest=None)

        return log_entry

    def process_log_entry(self, entry_raw: str):
        print(entry_raw, end='')
        self.check_errors(entry_raw)

        log_entry = self.parse_entry(entry_raw)
        self.custom_process_log_entry(log_entry)

    def custom_process_log_entry(self, log_entry: LogEntry):
        pass
