#!/usr/bin/env python3

import sys
import yaml
from common import *


if __name__ == '__main__':
    print("[INFO] Sort .yaml:")

    if len(sys.argv) - 1 == 2:
        SRC_FILE = sys.argv[1]
        DEST_FILE = sys.argv[2]
        print("     | SRC_FILE: ", SRC_FILE)
        print("     | DEST_FILE: ", DEST_FILE)
    else:
        raise Exception(f"Wrong number of arguments: ${len(sys.argv) - 1} < 2")

    yamlDict: dict = read_yaml_as_dict(SRC_FILE)  # python dict is sorted
    write_dict_as_yaml(DEST_FILE, yamlDict)
