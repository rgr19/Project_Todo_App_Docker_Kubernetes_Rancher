#!/usr/bin/env python3.7

import sys

from common import write_env_file, read_yaml_as_env_list, write_list_as_yaml

print("[INFO] Convert YAML to ENV:")

if len(sys.argv) - 1 >= 2:
    SRC_FILE = sys.argv[1]
    DEST_FILE = sys.argv[2]

    print("     | SRC_FILE: ", SRC_FILE)
    print("     | DEST_FILE: ", DEST_FILE)
else:
    raise Exception(f"Wrong number of arguments: {len(sys.argv) - 1} < 2")

envContent: list = read_yaml_as_env_list(SRC_FILE)
write_list_as_yaml(DEST_FILE, envContent)
