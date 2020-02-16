#!/usr/bin/env python3

import sys,os
from pprint import pprint

print("[INFO] Execute template concat:")

if len(sys.argv) - 1 >= 2:

	DEST_FILE=sys.argv[1]
	TEMP_FILE=sys.argv[2:]

	print("     | DEST_FILE: ", DEST_FILE)
	print("     | TEMPLATE_FILES: ")

	templatesText = []

	for tempFilePath in TEMP_FILE:
		print("          |", tempFilePath) 
		with open(tempFilePath, 'r') as tempFile:
			tempText = tempFile.read()
			templatesText.append(tempText)

	with open(DEST_FILE, 'w') as destFile:
		for tempText in templatesText:
			destFile.write(tempText)
else:
	raise Exception(f"Wrong number of arguments: ${len(sys.argv)-1} <= 2")
