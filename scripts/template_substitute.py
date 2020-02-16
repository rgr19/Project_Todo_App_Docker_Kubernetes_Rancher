#!/usr/bin/env python3

import sys,os
from pprint import pprint

if len(sys.argv) - 1 == 3:

	ENV_FILE=sys.argv[1]
	TEMP_FILE=sys.argv[2]
	DEST_FILE=sys.argv[3]	
	print("[INFO] Template substitute:")
	print("     | ENV_FILE: ", ENV_FILE)
	print("     | TEMP_FILE: ",TEMP_FILE)
	print("     | DEST_FILE: ", DEST_FILE)


	with open(ENV_FILE, 'r') as envFile, open(TEMP_FILE, 'r') as tempFile:
		envVars = envFile.read().strip().split()
		envMap = {}
		for kv in envVars:
			k,v = kv.split('=',1)
			envMap[k]=v
		
		os.environ.update(envMap)
		tempText = tempFile.read()

	with open(DEST_FILE, 'w') as destFile:
		destText = os.path.expandvars(tempText)
		destFile.write(destText)
else:
	raise Exception(f"Wrong number of arguments: ${len(sys.argv)-1}/3")
