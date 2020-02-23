from pprint import pprint
from typing import List
import datas
import yaml
import os


def is_yaml(f: str):
    return f.endswith('yaml') or f.endswith("yml")


def write_file(filePath, obj):
    if isinstance(obj, dict):
        write_dict_as_yaml(filePath, obj)
    elif isinstance(obj, list):
        write_list_as_text(filePath, obj)
    elif isinstance(obj, str):
        with open(filePath, 'w') as fp:
            fp.write(obj)


def write_list_as_text(destFilePath: str, filesContents: list) -> None:
    with open(destFilePath, 'w') as fp:
        for tempText in filesContents:
            print(tempText, file=fp)


def write_list_as_yaml(filePath: str, envList: list) -> None:
    envDict: dict = env_list_as_dict(envList)
    write_dict_as_yaml(filePath, envDict)


def write_dict_as_yaml(filePath: str, yamlDict: dict) -> None:
    with open(filePath, 'w') as fp:
        print(yaml.dump(yamlDict), file=fp)


def read_yaml_as_dict(filePath: str) -> dict:
    with open(filePath, 'r') as fp:
        text = fp.read().strip()
        dct = yaml.load(text, Loader=yaml.FullLoader)
    return dct


def write_env_file(filePath: str, envLines: list) -> None:
    with open(filePath, 'w') as fp:
        for line in envLines:
            print(line, file=fp)


def env_list_as_dict(envList: list):
    envDict: dict = {}
    for line in envList:
        if line[0] != "#":
            var, val = line.split('=', maxsplit=1)
            envDict[var] = val
    return envDict


def read_env_file_as_dict(filePath: str) -> dict:
    with open(filePath, 'r') as fp:
        envLines = fp.read().strip().splitlines()
    envVars: dict = env_list_as_dict(envLines)
    return envVars


def text_expand_vars(tempText: str, envDict: dict) -> str:
    osEnvironCopy = os.environ.copy()
    os.environ.clear()
    os.environ.update(envDict)
    destText = os.path.expandvars(tempText)
    os.environ.clear()
    os.environ.update(osEnvironCopy)
    return destText


def text_expand_vars_by_envfile(envFilePath, text: str) -> str:
    if is_yaml(envFilePath):
        envDict: dict = read_yaml_as_env_dict(envFilePath)
    else:
        envDict: dict = read_env_file_as_dict(envFilePath)
    envDict = eval(text_expand_vars(str(envDict), envDict))
    return text_expand_vars(text, envDict)


def file_expand_vars(envVars: dict, tempFilePath: str) -> str:
    text = open(tempFilePath, 'r').read()
    return text_expand_vars(text, envVars)


def file_expand_vars_by_envfile(envFilePath: str, tempFilePath: str) -> str:
    text = open(tempFilePath, 'r').read()
    return text_expand_vars_by_envfile(envFilePath, text)


def convert_yaml_to_env(tree: dict, key: str = None) -> List[str]:
    if not isinstance(tree, dict):  # , list, tuple, set)):
        return [f'{key}={tree}']

    out = []

    # if isinstance(tree, dict):
    for k in tree.keys():
        o = convert_yaml_to_env(tree[k], k)
        for pair in o:
            out.append(pair)

    # elif isinstance(tree, (list, tuple, set)):

    paths = []
    for path in out:
        if key is not None:
            path = f'{key}_{path}'
        paths.append(path)
    return paths


def convert_env_to_yaml(varsDict: dict) -> dict:
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


def read_yaml_as_env_list(yamlFilePath: str) -> list:
    yamlDct: dict = read_yaml_as_dict(yamlFilePath)
    envContent: list = convert_yaml_to_env(yamlDct)
    return envContent


def read_yaml_as_env_dict(yamlFilePath: str) -> dict:
    yamlList: list = read_yaml_as_env_list(yamlFilePath)
    yamlDict: dict = env_list_as_dict(yamlList)
    return yamlDict


def concat_yamls_content(yamlsPaths: List[str]) -> dict:
    envsList: list = []
    for tempFilePath in yamlsPaths:
        envsList.extend(read_yaml_as_env_list(tempFilePath))
    envsDict: dict = env_list_as_dict(envsList)
    return envsDict


def concat_files(filesPaths: List[str]) -> list:
    filesContents: list = []
    for tempFilePath in filesPaths:
        with open(tempFilePath, 'r') as tempFile:
            tempText: str = tempFile.read()
            filesContents.append(tempText)
    return filesContents
