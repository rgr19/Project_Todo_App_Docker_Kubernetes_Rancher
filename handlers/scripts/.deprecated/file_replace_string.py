#!/usr/bin/env python3.7

import sys

print("[INFO] Replace CHAR_OLD by CHAR_NEW in INPUT_TEXT:")
if len(sys.argv) - 1 == 4:
    SRC_FILE = sys.argv[1]
    DEST_FILE = sys.argv[2]
    STR_OLD = sys.argv[3]
    STR_NEW = sys.argv[4]

    print("     | SRC_FILE: ", SRC_FILE)
    print("     | DEST_FILE: ", DEST_FILE)
    print("     | STR_OLD: ", STR_OLD)
    print("     | STR_NEW: ", STR_NEW)

else:
    raise Exception(f"Wrong number of arguments: {len(sys.argv) - 1} < 3")

with open(SRC_FILE, 'r') as fp:
    srcText = fp.read()

destText = srcText
STR_OLD = STR_OLD.split()
STR_NEW = STR_NEW.split()

assert(len(STR_OLD) == len(STR_NEW))

for old, new in zip(STR_OLD, STR_NEW):
    destText = destText.replace(old, new)

with open(DEST_FILE, 'w') as fp:
    print(destText, file=fp)
