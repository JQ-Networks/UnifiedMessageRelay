from typing import List, Union, Dict
import logging


# test attribute
def test_attribute(config: Dict, attributes: List[str], logger: logging.Logger) -> Union[str, None]:
    """
    Test if attributes exist in config
    :param config: config file
    :param attributes: list of attribute strings
    :param logger: log to this logger
    :return: str for first missing attribute, or None for Okay
    """
    for attr in attributes:
        if attr not in config:
            logger.error(f'{attr} not found in config.yaml')
            exit(-1)
    return None
