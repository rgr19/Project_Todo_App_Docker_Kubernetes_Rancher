#!/usr/bin/env python3.7

#TODO

import sys, os
from pprint import pprint
import yaml
import datas

env = open('.env', 'r').read().strip().splitlines()
treeDct = datas.autodict()

for l in env:
    if l[0] == '#': continue
    variable, value = l.split('=')
    dctPath = dctLayerPrev = dctLayerNext = treeDct
    path = variable.split('_')
    for layer in path:
        dctLayerPrev = dctLayerNext
        dctLayerNext = dctLayerNext[layer]
    dctLayerPrev[layer] = value

treeDict = eval(str(treeDct))

print(yaml.dump(treeDict))

print("[INFO] Convert .env to .yaml:")

if len(sys.argv) - 1 >= 2:
    ENV_FILE = sys.argv[1]
    YML_FILE = sys.argv[2]
    if len(sys.argv) - 1 > 2:
        PREFIXES = sys.argv[3:]
    else:
        PREFIXES = []


else:
    raise Exception(f"Wrong number of arguments: ${len(sys.argv) - 1} <= 2")

print("     | ENV_FILE: ", ENV_FILE)
print("     | YML_FILE: ", YML_FILE)
print("     | PREFIXES: ", PREFIXES)

with open(ENV_FILE, 'r') as envFile:
    envText = envFile.read()

envText = envText.strip().splitlines()
envMap = {p: {} for p in PREFIXES}

for line in envText:
    foundPrefix = None
    for prefix in PREFIXES:
        if prefix in line:
            line = line.replace(f"{prefix}_", "")
            foundPrefix = prefix
            break
    k, v = line.split('=')
    if foundPrefix:
        envMap[foundPrefix][k] = v
    else:
        envMap[k] = v

with open(YML_FILE, 'w') as destFile:
    print(yaml.dump(envMap), file=destFile)
