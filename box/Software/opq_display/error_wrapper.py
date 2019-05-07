import logging
import os

logger = logging.getLogger("opq_display_client")
logging.basicConfig(
    format="[%(levelname)s][%(asctime)s][{} %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s".format(
        os.getpid()))
logger.setLevel(logging.DEBUG)


def silence(func):
    def wrapper_silence_error(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            logger.error("%s", str(e))
    return wrapper_silence_error
