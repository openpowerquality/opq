"""
This module provides functionality for working with Mauka configuration files.
"""

import json
import typing


class MaukaConfig:
    """
    An instance of a Mauka config that will throw when a key doesn't exist (unless a default is provided)
    """

    def __init__(self, config_dict: typing.Dict[str, typing.Union[str, int, float, bool]]):
        self.config_dict = config_dict

    def get(self, key: str, default: typing.Union[str, int, float, bool] = None) -> typing.Union[str, int, float, bool]:
        """
        Returns the value in the configuration associated with this key.
        :param key: The key to search for.
        :param default: The default value to provide if the key is not in the configuration.
        :return: Either the configuration value, the default value, or throw.
        """
        if key in self.config_dict:
            return self.config_dict[key]
        else:
            if default is not None:
                return default
            else:
                raise KeyError("Key {} was not found in config and no default was supplied.".format(key))


def from_file(path: str) -> MaukaConfig:
    """
    Loads a Mauka config from a file.
    :param path: The path to the configuration.
    :return: The MaukaConfig
    """
    try:
        with open(path, "r") as fin:
            return MaukaConfig(json.load(fin))
    except FileNotFoundError:
        raise FileNotFoundError("Error opening config at path {}".format(path))


def from_dict(config_dict: typing.Dict[str, typing.Union[str, int, float, bool]]) -> MaukaConfig:
    """
    Create an instance of a MaukaConfig from a dictionary.
    :param config_dict: Dictionary of config values.
    :return: An instance of a MaukaConfig.
    """
    return MaukaConfig(config_dict)
