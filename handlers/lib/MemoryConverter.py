import enum
import logging
import math

logger = logging.getLogger(__name__)

logger.info("Hello logging!")


# Enum for size units
class MEMORY_UNIT(enum.Enum):
    Kb = 2
    Mb = 3
    Gb = 4


class MEMORY_STRING:
    class K8S:
        Ki = 'Ki'
        Mi = 'Mi'
        Gi = 'Gi'

    class DOCKER:
        k = 'k'
        m = 'm'
        g = 'g'

    class AWS:
        pass

    K8S_DOCKER = {
        K8S.Ki: DOCKER.k,
        K8S.Mi: DOCKER.m,
        K8S.Gi: DOCKER.g,
    }
    K8S_AWS = {
        K8S.Ki: MEMORY_UNIT.Kb,
        K8S.Mi: MEMORY_UNIT.Mb,
        K8S.Gi: MEMORY_UNIT.Gb,
    }


class MemoryConverter:
    Kb: int = 1024
    Mb: int = 1024 * Kb
    Gb: int = 1024 * Mb

    UNIT = MEMORY_UNIT
    DOCKER = MEMORY_STRING.DOCKER
    K8S = MEMORY_STRING.K8S
    AWS = MEMORY_STRING.AWS
    K8S_DOCKER: dict = MEMORY_STRING.K8S_DOCKER
    K8S_AWS: dict = MEMORY_STRING.K8S_AWS

    @staticmethod
    def convert_unit(sizeInBytes: int, unit: UNIT) -> int:
        if unit == unit.Kb:
            return math.ceil(sizeInBytes / MemoryConverter.Kb)
        elif unit == unit.Mb:
            return math.ceil(sizeInBytes / MemoryConverter.Mb)
        elif unit == unit.Gb:
            return math.ceil(sizeInBytes / MemoryConverter.Gb)
        else:
            return sizeInBytes

    @staticmethod
    def convert_k8s_to_docker(size: str) -> str:
        for unit in MemoryConverter.K8S_DOCKER:
            if unit in size:
                return size.replace(unit, MemoryConverter.K8S_DOCKER[unit])

    @staticmethod
    def convert_k8s_to_aws(size: str) -> int:
        for unit in MemoryConverter.K8S_AWS:
            if unit in size:
                size: int = int(size.replace(unit, ''))
                return MemoryConverter.convert_unit(size, MemoryConverter.K8S_AWS[unit])
