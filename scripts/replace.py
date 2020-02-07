#!/usr/bin/env python3

import sys

inputText = sys.argv[1]
textList = inputText.strip().split()
flatText=','.join(textList)
print(flatText)
