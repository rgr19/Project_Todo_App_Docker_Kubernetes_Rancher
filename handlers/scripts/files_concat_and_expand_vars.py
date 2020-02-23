#!/usr/bin/env python3

import sys
from typing import Union, Dict, List

from common import text_expand_vars_by_envfile, write_file, write_dict_as_yaml
from files_concat import files_content_concat

if __name__ == '__main__':
    print("[INFO] Execute template concat and expand vars:")

    if len(sys.argv) - 1 >= 3:
        ENV_FILE = sys.argv[1]
        DEST_FILE = sys.argv[2]
        FILES_LIST = sys.argv[3:]
        print("     | ENV_FILE: ", ENV_FILE)
        print("     | DEST_FILE: ", DEST_FILE)
        print("     | FILES_LIST: ")
        for text in FILES_LIST:
            print("          |", text)
    else:
        raise Exception(f"Wrong number of arguments: ${len(sys.argv) - 1} < 3")

    filesContent: Union[Dict, List[str]] = files_content_concat(FILES_LIST)
    filesContent: str = str(filesContent)
    filesContent: str = text_expand_vars_by_envfile(ENV_FILE, filesContent)
    filesContent: dict = eval(filesContent)
    write_dict_as_yaml(DEST_FILE, filesContent)
