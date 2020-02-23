#!/usr/bin/env python3

import sys

# print("[INFO] Replace CHAR_OLD by CHAR_NEW in INPUT_TEXT:")
if len(sys.argv) - 1 >= 3:
    CHAR_OLD = sys.argv[1]
    CHAR_NEW = sys.argv[2]
    INPUT_TEXT = sys.argv[3:]
    # print("     | CHAR_OLD: ", CHAR_OLD)
    # print("     | CHAR_NEW: ", CHAR_NEW)
    # print("     | INPUT_TEXT: BEGIN")
    # for text in INPUT_TEXT:
        # print(text)
    # print("     | INPUT_TEXT: END")

else:
    raise Exception(f"Wrong number of arguments: {len(sys.argv) - 1} < 3")

for text in INPUT_TEXT:
    text = text.replace(CHAR_OLD, CHAR_NEW)
    print(text)
