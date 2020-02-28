#!/usr/bin/env python3.7

import sys

from common import file_expand_vars_by_envfile, write_file

if __name__ == '__main__':
    print("[INFO] Template substitute:")
    if len(sys.argv) - 1 == 2:
        ENV_FILE = sys.argv[1]
        TEMP_FILE = DEST_FILE = sys.argv[2]
        print("     | ENV_FILE: ", ENV_FILE)
        print("     | TEMP_FILE: ", TEMP_FILE)
        print("     | DEST_FILE: ", DEST_FILE)
    elif len(sys.argv) - 1 == 3:
        ENV_FILE = sys.argv[1]
        TEMP_FILE = sys.argv[2]
        DEST_FILE = sys.argv[3]
        print("     | ENV_FILE: ", ENV_FILE)
        print("     | TEMP_FILE: ", TEMP_FILE)
        print("     | DEST_FILE: ", DEST_FILE)
    else:
        raise Exception(f"Wrong number of arguments: ${len(sys.argv) - 1}/3")

    expandedText: str = file_expand_vars_by_envfile(ENV_FILE, TEMP_FILE)
    write_file(DEST_FILE, expandedText)
