#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time
import argparse

import psutil


def yield_processes():
    for pid in psutil.pids():
        try:
            p = psutil.Process(pid)
        except:
            continue

        try:
            yield (p.memory_percent(), p)
        except psutil._exceptions.NoSuchProcess:
            pass


def kill_process_eating_most_of_the_memory():
    processes = sorted(yield_processes())
    process = processes.pop()[-1]

    try:
        percent = process.memory_percent()
        process.terminate()
        print "killed %s (%.2f%%)" % (process.name(), percent)
    except psutil._exceptions.NoSuchProcess:
        pass


def kill_memory_eaters(percent):
    while True:
        free_memory = 100 - psutil.virtual_memory().percent
        if free_memory < percent:
            kill_process_eating_most_of_the_memory()

        yield


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--percent",
        default=5,
        type=int,
        help="Kill the most memory hungry process when free memory drops bellow this limit. Default %(default)s%%."
    )
    parser.add_argument(
        "-t",
        "--time",
        default=5,
        type=int,
        help="Sleep TIME seconds between checks. Default %(default)s seconds."
    )

    args = parser.parse_args()

    for _ in kill_memory_eaters(args.percent):
        time.sleep(args.time)
