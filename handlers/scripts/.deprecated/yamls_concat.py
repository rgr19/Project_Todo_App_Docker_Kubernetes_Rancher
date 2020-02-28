#!/usr/bin/env python3.7

import sys
from typing import List, Dict, Union

from common import concat_yamls_content, convert_env_to_yaml, write_file




if __name__ == '__main__':
    print("[INFO] Yaml files concat:")

    if len(sys.argv) - 1 >= 2:

        DEST_FILE = sys.argv[1]
        FILES_LIST = sys.argv[2:]
        print("     | DEST_FILE: ", DEST_FILE)
        print("     | FILES_LIST: ")
        for text in FILES_LIST:
            print("          |", text)
    else:
        raise Exception(f"Wrong number of arguments: ${len(sys.argv) - 1} <= 2")

    filesContent: Union[Dict, List[str]] = yaml_content_concat(FILES_LIST)
    write_file(DEST_FILE, filesContent)
