#!/usr/bin/env python3.7

import sys

from common import write_env_file, read_yaml_as_env_list

print("[INFO] Convert YAML to ENV:" )

if len(sys.argv) - 1 >= 2:
    YML_FILE = sys.argv[1]
    ENV_FILE = sys.argv[2]

    print("     | YML_FILE: ", YML_FILE)
    print("     | ENV_FILE: ", ENV_FILE)
else:
    raise Exception(f"Wrong number of arguments: {len(sys.argv) - 1} < 2")

envContent: list = read_yaml_as_env_list(YML_FILE)
write_env_file(ENV_FILE, envContent)
