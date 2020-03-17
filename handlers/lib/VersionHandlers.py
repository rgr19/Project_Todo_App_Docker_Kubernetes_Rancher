import os
import re

from handlers.lib.Logger import Logger

logger = Logger.build(__name__)

NEXT = 'NEXT'
LAST = 'LAST'
PREV = 'PREV'


def version_parser(v):
	versionPattern = r'\d+(=?\.(\d+(=?\.(\d+)*)*)*)*'
	regexMatcher = re.compile(versionPattern)
	return regexMatcher.search(v).group(0)


def parse_project_version(version: str):
	cacheFile = '.project_versions_used'
	if not os.path.exists(cacheFile):
		open(cacheFile, 'w').write('')
		prevVersions = set()
	else:
		prevVersions = open(cacheFile, 'r').read().strip()
		prevVersions = set(filter(bool, prevVersions.splitlines()))

	if version == NEXT or version == LAST or version == PREV:
		versionTuple = lastVersionTuple = (0, 0, 1)
		for x in range(100):
			for y in range(100):
				for z in range(100):
					tempVersion = f'{x}.{y}.{z}'
					if tempVersion not in prevVersions:
						if version == PREV:
							if z:
								versionTuple = x, y, z - 1
							elif y:
								versionTuple = x, y - 1, z
							elif x:
								versionTuple = x - 1, y, z
							else:
								versionTuple = x, y, z
						if version == NEXT:
							versionTuple = x, y, z
						elif version == LAST:
							versionTuple = lastVersionTuple
						break
					lastVersionTuple = x, y, z
				else:
					continue  # only executed if the inner loop did NOT break
				break  # only executed if the inner loop DID break
			else:
				continue  # only executed if the inner loop did NOT break
			break  # only executed if the inner loop DID break
		version = '.'.join(map(str, versionTuple))
	else:
		if not bool(version_parser(version)):
			raise ValueError("Project version do not match pattern x[.x]")

	prevVersions.add(version)
	with open(cacheFile, 'w') as fp:
		for v in prevVersions:
			print(v, file=fp)
	return version


def parse_images_version(version: str):
	cacheFile = '.images_versions_used'
	versionTuple = lastVersionTuple = (0, 1)

	if not os.path.exists(cacheFile):
		open(cacheFile, 'w').write('')
		prevVersions = set()
	else:
		prevVersions = open(cacheFile, 'r').read().strip()
		prevVersions = set(filter(bool, prevVersions.splitlines()))

	if version == NEXT or version == LAST or version == PREV:
		for x in range(100):
			for y in range(100):
				tempVersion = f'{x}.{y}'
				if tempVersion not in prevVersions:
					if tempVersion == PREV:
						if y:
							versionTuple = x, y - 1
						elif x:
							versionTuple = x - 1, y
						else:
							versionTuple = x, y
					if version == NEXT:
						versionTuple = x, y
					elif version == LAST:
						versionTuple = lastVersionTuple
					break
				lastVersionTuple = x, y
			else:
				continue  # only executed if the inner loop did NOT break
			break  # only executed if the inner loop DID break
		version = '.'.join(map(str, versionTuple))
	else:
		if not bool(version_parser(version)):
			raise ValueError("Project version do not match pattern x[.x]")

	prevVersions.add(version)
	with open(cacheFile, 'w') as fp:
		for v in prevVersions:
			print(v, file=fp)
	return version
