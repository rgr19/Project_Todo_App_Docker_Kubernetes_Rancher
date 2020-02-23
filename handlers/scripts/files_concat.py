#!/usr/bin/env python3

import sys
from typing import List, Dict, Union

from common import concat_files, write_file

if __name__ == '__main__':
    print("[INFO] Files concat:")

    if len(sys.argv) - 1 >= 2:

        DEST_FILE = sys.argv[1]
        FILES_LIST = sys.argv[2:]
        print("     | DEST_FILE: ", DEST_FILE)
        print("     | FILES_LIST: ")
        for text in FILES_LIST:
            print("          |", text)
    else:
        raise Exception(f"Wrong number of arguments: ${len(sys.argv) - 1} <= 2")

    filesContent: Union[Dict, List[str]] = concat_files(FILES_LIST)
    write_file(DEST_FILE, filesContent)
