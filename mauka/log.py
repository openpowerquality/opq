"""
Utility module for logging.
"""

import logging
import os


def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger.
    :param name: The name of the logger.
    :return: An instantiated logger.
    """
    logger = logging.getLogger(name)
    logging.basicConfig(
        format="[%(levelname)s][%(asctime)s][{} %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s".format(
            os.getpid()))
    logger.setLevel(logging.DEBUG)
    return logger


def maybe_debug(msg: str, mauka_plugin):
    """
    Optionally prints a debug message depending on an optional plugin.
    :param msg: The message to debug.
    :param mauka_plugin: An optional plugin instance.
    """
    if mauka_plugin is not None:
        mauka_plugin.debug(msg)
