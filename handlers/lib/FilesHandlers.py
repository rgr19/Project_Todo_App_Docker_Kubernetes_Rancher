#!/usr/bin/env python3.7
import logging
import os
from typing import List, Iterable

import datas
import yaml

logger = logging.getLogger(__name__)

logger.info("Hello logging!")


class File(object):

	@staticmethod
	def is_yaml(f: str):
		return f.endswith('yaml') or f.endswith("yml")


class FileRead(File):

	@staticmethod
	def text(path: str):
		return open(path, 'r').read()

	@staticmethod
	def multiple(filesPaths: Iterable[str]) -> list:
		filesContents: list = []
		for tempFilePath in filesPaths:
			with open(tempFilePath, 'r') as tempFile:
				tempText: str = tempFile.read()
				filesContents.append(tempText)
		return filesContents


class FileWrite(File):

	def __init__(self, filePath, obj):
		with open(filePath, 'w') as fp:
			fp.write(obj)

	@staticmethod
	def guess_kind(filePath, obj):
		if isinstance(obj, dict):
			YamlWrite.from_dict(filePath, obj)
		elif isinstance(obj, list):
			FileWrite.from_list(filePath, obj)
		elif isinstance(obj, str):
			FileWrite(filePath, obj)

	@staticmethod
	def from_list(fileDest: str, filesContents: list) -> None:
		with open(fileDest, 'w') as fp:
			for tempText in filesContents:
				print(tempText, file=fp)


class FileReadWrite(File):

	def __init__(self, fileSrc: str, fileDest: str):
		fileContent: str = FileRead.text(fileSrc)
		FileWrite.guess_kind(fileDest, fileContent)

	@staticmethod
	def concat(fileDest: str, *srcFilesPaths: str):
		filesContent: List[str] = FileRead.multiple(srcFilesPaths)
		FileWrite.guess_kind(fileDest, filesContent)


class FileExpandvars(object):

	@staticmethod
	def from_keywords(tempFilePath: str, envVars: dict) -> str:
		text = open(tempFilePath, 'r').read()
		return TextExpandvars.in_text(text, envVars)

	@staticmethod
	def by_envdir(envDirPath: str, tempFilePath: str) -> str:
		envDirVars: dict = EnvRead.dir_to_dict(envDirPath)
		return FileExpandvars.from_keywords(tempFilePath, envDirVars)

	@staticmethod
	def by_envfile(envFilePath: str, tempFilePath: str) -> str:
		text = open(tempFilePath, 'r').read()
		return TextExpandvars.by_envfile(envFilePath, text)


class FileExpandvarsWrite(object):

	@staticmethod
	def by_keywords_to_file(tempFilePath: str, fileDest: str, **envVars: str) -> None:
		if not envVars:
			raise ValueError("No keywords provided to expand vars from.")
		destText: str = FileExpandvars.from_keywords(tempFilePath, envVars)
		FileWrite.guess_kind(fileDest, destText)

	@staticmethod
	def by_envdir_to_file(envDirPath: str, tempFilePath: str, fileDest: str) -> None:
		envDirVars: dict = EnvRead.dir_to_dict(envDirPath)
		expandedText: str = FileExpandvars.from_keywords(tempFilePath, envDirVars)
		FileWrite.guess_kind(fileDest, expandedText)

	@staticmethod
	def by_envfile_to_file(envFilePath: str, tempFilePath: str, fileDest: str) -> None:
		tempFileText: str = open(tempFilePath, 'r').read()
		expandedText: str = TextExpandvars.by_envfile(envFilePath, tempFileText)
		FileWrite.guess_kind(fileDest, expandedText)


class TextExpandvars(object):
	@staticmethod
	def in_text(tempText: str, envVars: dict) -> str:
		osEnvironCopy = os.environ.copy()
		os.environ.clear()
		os.environ.update(envVars)
		destText = os.path.expandvars(tempText)
		os.environ.clear()
		os.environ.update(osEnvironCopy)
		return destText

	@staticmethod
	def by_envfile(envFilePath, text: str) -> str:
		if File.is_yaml(envFilePath):
			envDict: dict = YamlRead.as_env_flat_dict(envFilePath)
		else:
			envDict: dict = EnvRead.as_dict(envFilePath)
		envDict = eval(TextExpandvars.in_text(str(envDict), envDict))
		return TextExpandvars.in_text(text, envDict)


class Env(object):
	@staticmethod
	def dict_to_env_lines(tree: dict, key: str = None) -> List[str]:
		if not isinstance(tree, dict):  # , list, tuple, set)):
			return [f'{key}={tree}']
		out = []
		for k in tree.keys():
			o = Env.dict_to_env_lines(tree[k], k)
			for pair in o:
				out.append(pair)
		paths = []
		for path in out:
			if key is not None:
				path = f'{key}_{path}'
			paths.append(path)
		return paths

	@staticmethod
	def list_as_flat_dict(envList: list):
		envDict: dict = {}
		for line in envList:
			if line[0] != "#":
				var, val = line.split('=', maxsplit=1)
				envDict[var] = val
		return envDict

	@staticmethod
	def to_yaml(varsDict: dict) -> dict:
		treeDct = datas.autodict()
		for var, val in varsDict.items():
			dctLayerPrev = dctLayerNext = treeDct
			path = layer = var.split('_')
			for layer in path:
				dctLayerPrev = dctLayerNext
				dctLayerNext = dctLayerNext[layer]
			dctLayerPrev[layer] = val

		treeDct = eval(str(treeDct))

		return treeDct


class EnvRead(object):

	@staticmethod
	def as_dict(filePath: str) -> dict:
		with open(filePath, 'r') as fp:
			envLines = fp.read().strip().splitlines()
		envVars: dict = Env.list_as_flat_dict(envLines)
		return envVars

	@staticmethod
	def dir_to_dict(envDir):
		envVars: dict = {}
		for root, dirs, files in os.walk(envDir):
			for file in files:
				filePath = os.path.join(root, file)
				if os.path.isfile(filePath):
					envVars[file] = open(filePath, 'r').read().strip()
				else:
					raise ValueError(f"No such file {filePath}")
		return envVars


class EnvWrite(Env):
	def __init__(self, filePath: str, envLines: list) -> None:
		with open(filePath, 'w') as fp:
			for line in envLines:
				print(line, file=fp)

	@staticmethod
	def from_dict(envVars: dict, fileDest: str) -> None:
		envVars: list = Env.dict_to_env_lines(envVars)
		EnvWrite(fileDest, envVars)


class YamlRead(object):
	@staticmethod
	def as_dict(filePath: str) -> dict:
		with open(filePath, 'r') as fp:
			text = fp.read().strip()
			dct = yaml.load(text, Loader=yaml.loader.BaseLoader)  # Loader=yaml.FullLoader)
		return dct

	@staticmethod
	def as_env_list(yamlFilePath: str) -> list:
		yamlDct: dict = YamlRead.as_dict(yamlFilePath)
		envContent: list = Env.dict_to_env_lines(yamlDct)
		return envContent

	@staticmethod
	def concat_flat(yamlsPaths: Iterable[str]) -> dict:
		envsList: list = []
		for tempFilePath in yamlsPaths:
			envContent: list = YamlRead.as_env_list(tempFilePath)
			envsList.extend(envContent)
		envsDict: dict = Env.list_as_flat_dict(envsList)
		return envsDict

	@staticmethod
	def concat(*filesList: str) -> dict:
		assert (len(filesList) > 0)
		envDict: dict = YamlRead.concat_flat(filesList)
		return Env.to_yaml(envDict)

	@staticmethod
	def as_env_flat_dict(yamlFilePath: str) -> dict:
		yamlList: list = YamlRead.as_env_list(yamlFilePath)
		yamlDict: dict = Env.list_as_flat_dict(yamlList)
		return yamlDict


class YamlWrite(object):
	@staticmethod
	def from_dict(filePath: str, yamlDict: dict) -> None:
		with open(filePath, 'w') as fp:
			print(yaml.dump(yamlDict, default_style='"'), file=fp, )

	@staticmethod
	def from_env_list(filePath: str, envList: list) -> None:
		envDict: dict = Env.list_as_flat_dict(envList)
		YamlWrite.from_dict(filePath, envDict)

	@staticmethod
	def as_env(fileSrc: str, fileDest: str):
		envVars: list = YamlRead.as_env_list(fileSrc)
		EnvWrite(fileDest, envVars)


class YamlRewrite(object):

	def __init__(self, filePath):
		yamlDict: dict = YamlRead.as_dict(filePath)  # python dict is sorted
		YamlWrite.from_dict(filePath, yamlDict)

	@staticmethod
	def multiple_from_dir(dirPath: str):
		for root, dirs, files in os.walk(dirPath):
			for f in files:
				if f.endswith('yaml') or f.endswith('yml'):
					filePath = os.path.join(root, f)
					YamlRewrite(filePath)

	@staticmethod
	def flat(fileSrc: str, fileDest: str):
		envContent: list = YamlRead.as_env_list(fileSrc)
		YamlWrite.from_env_list(fileDest, envContent)


class YamlConcatWrite(object):

	def __init__(self, destFile, *filesList: str) -> None:
		filesContent: dict = YamlRead.concat(*filesList)
		FileWrite.guess_kind(destFile, filesContent)

	@staticmethod
	def as_is(fileDest: str, *filesSrc: str):
		FileReadWrite.concat(fileDest, *filesSrc)

	@staticmethod
	def multiple_as_is_from_dir(fileDest: str, dirPath: str):
		filesSrc: list = []
		for root, dirs, files in os.walk(dirPath):
			for f in files:
				if f.endswith('yaml') or f.endswith('yml'):
					filePath = os.path.join(root, f)
					filesSrc.append(filePath)
		YamlConcatWrite.as_is(fileDest, *filesSrc)
