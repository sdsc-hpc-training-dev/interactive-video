#!/usr/local/bin/python

import sys
import re
from glob import glob
from collections import defaultdict

def main():
    FIND = sys.argv[1] if len(sys.argv) > 1 else None

    if not FIND:
        print("Example usage: ./stats.py hpc_user_training_2021")
        return

    LOG_DIR = "/misc/www/misc/apache/logs/education.sdsc.edu"
    LOG_FILES = "access.education.sdsc.edu.20210**"
    LOG_PATH = LOG_DIR + "/" + LOG_FILES

    print("Reading log files from dir: " + LOG_PATH)

    regex = re.compile("(\d+\.\d+\.\d+\.\d+) .+ \"GET .+\/" + FIND + "\/(\w+[0-9]+)? ")

    unique_visitors = defaultdict(lambda: defaultdict(int))

    total_files = 0
    for name in glob(LOG_PATH):
        total_files += 1
        f = open(name)
        for line in f:
            match = re.search(regex, line)
            if not match:
                continue

            ip, path = match.groups()
            unique_visitors[ip][path or "index"] += 1
        f.close()

    print("Processed %i files" % total_files)

    def key_func(k):
        match = re.search(r"(\d+)$", k)
        if match:
            return int(match.groups()[0])
        else:
            return -1

    all_path = defaultdict(int)

    print("Unique visitors: %i" % len(unique_visitors))
    for ip in unique_visitors:
        print(ip + ": ")

        counter = unique_visitors[ip]
        keys = sorted(counter.keys(), key = key_func)
        for index in keys:
            all_path[index] += 1
            print("  %s: %i" % (index, counter[index]))

    print("All path hits: ")

    keys = sorted(all_path.keys(), key = key_func)
    for path in keys:
        print("  %s: %i" % (path, all_path[path]))

if __name__ == "__main__":
    main()