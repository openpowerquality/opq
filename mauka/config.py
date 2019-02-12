"""
This module provides functionality for working with Mauka configuration files.
"""

import json
import os
import typing

ConfigValueType = typing.Union[str, int, float, bool]
ConfigType = typing.Dict[str, ConfigValueType]


class MaukaConfig:
    """
    An instance of a Mauka config that will throw when a key doesn't exist (unless a default is provided)
    """

    def __init__(self, config_dict: ConfigType):
        self.config_dict = self.replace_env(config_dict)

    def replace_env(self, config_dict: ConfigType) -> ConfigType:
        """
        This function parses values from the config that are strings and start with a question mark "?" and replaces
        them with the value set in the environment using the name of everything after the question mark.
        :param config_dict: The configuration dictionary.
        :return: A configuration dictionary with environment variables substituted for marked config entries.
        """
        replacement_dict = {}
        for key, value in config_dict.items():
            if type(value) == str and value.startswith("?"):
                env_name = value[:1]
                replacement = os.getenv(env_name)
                if replacement is None:
                    raise RuntimeError("Environment variable with name %s was not found in the environment." % env_name)

                replacement_dict[key] = replacement
            else:
                replacement_dict[key] = value

        return replacement_dict

    def get(self, key: str, default: ConfigValueType = None) -> ConfigValueType:
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

    def __getitem__(self, item):
        return self.get(item)


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


def from_dict(config_dict: ConfigType) -> MaukaConfig:
    """
    Create an instance of a MaukaConfig from a dictionary.
    :param config_dict: Dictionary of config values.
    :return: An instance of a MaukaConfig.
    """
    return MaukaConfig(config_dict)
