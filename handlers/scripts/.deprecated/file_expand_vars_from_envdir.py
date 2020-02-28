#!/usr/bin/env python3.7

import sys, os
from pprint import pprint

from common import file_expand_vars_by_envfile, write_file, read_yaml_as_env_list, text_expand_vars, file_expand_vars





if __name__ == '__main__':
    print("[INFO] Expand vars in SRC_YAML with ENV_DIR files and save to DEST_YAML:")
    if len(sys.argv) - 1 == 3:
        ENV_DIR = sys.argv[1]
        SRC_FILE = sys.argv[2]
        DEST_FILE = sys.argv[3]
        print("     | ENV_FILE: ", ENV_DIR)
        print("     | TEMP_FILE: ", SRC_FILE)
        print("     | DEST_FILE: ", DEST_FILE)
    else:
        print("     | ENV_FILE: ??", )
        print("     | TEMP_FILE: ??", )
        print("     | DEST_FILE: ??", )
        raise Exception(f"Wrong number of arguments: ${len(sys.argv) - 1}/3")

    envDirVars: dict = read_env_dir_to_dict(ENV_DIR)
    destText: str = file_expand_vars(envDirVars, SRC_FILE)
    write_file(DEST_FILE, destText)

