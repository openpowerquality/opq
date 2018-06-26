import json
import typing

ConfigValueType = typing.Union[str, int, float, bool]
ConfigType = typing.Dict[str, ConfigValueType]


class MaukaConfig:
    def __init__(self, config_dict: ConfigType):
        self.config_dict = config_dict

    def get(self, key: str, default: ConfigValueType = None) -> ConfigValueType:
        if key in self.config_dict:
            return self.config_dict[key]
        else:
            if default is not None:
                return default
            else:
                raise KeyError("Key {} was not found in config and no default was supplied.".format(key))


def from_file(path: str) -> MaukaConfig:
    try:
        with open(path, "r") as fin:
            return MaukaConfig(json.load(fin))
    except FileNotFoundError:
        raise FileNotFoundError("Error opening config at path {}".format(path))


def from_dict(config_dict: ConfigType) -> MaukaConfig:
    return MaukaConfig(config_dict)
