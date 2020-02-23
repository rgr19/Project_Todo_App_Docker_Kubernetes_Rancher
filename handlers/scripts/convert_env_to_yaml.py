#!/usr/bin/env python3
import sys

from common import convert_env_to_yaml, write_dict_as_yaml, read_env_file_as_dict

if __name__ == '__main__':

    print("[INFO] Convert ENV to YAML:")

    if len(sys.argv) - 1 >= 2:
        ENV_FILE = sys.argv[1]
        YML_FILE = sys.argv[2]
        CHAR = "_"
        if len(sys.argv) - 1 == 3:
            CHAR = sys.argv[3]
        print("     | YML_FILE: ", YML_FILE)
        print("     | ENV_FILE: ", ENV_FILE)

    else:
        raise Exception(f"Wrong number of arguments: {len(sys.argv) - 1} < 2")

    envVars: dict = read_env_file_as_dict(ENV_FILE)
    yamlDict: dict = convert_env_to_yaml(envVars)
    write_dict_as_yaml(YML_FILE, yamlDict)
