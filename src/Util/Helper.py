from typing import List, Union, Dict, Callable
import logging
from janus import Queue
from Core.UMRType import UnifiedMessage
from Core.UMRLogging import getLogger
import os
import sys
import imageio

logger = getLogger('Util.Helper')

# test attributes in config.yaml
def check_attribute(config: Dict, attributes: List[str], logger: logging.Logger) -> Union[str, None]:
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


def assemble_message(message: UnifiedMessage) -> str:
    """
    assemble text of the message to a single string
    :param message: UnifiedMessage to assemble
    :return: result string
    """
    return ''.join(map(lambda x: x.text, message.message))


# async put new task to janus queue
async def janus_queue_put_async(_janus_queue: Queue, func: Callable, *args, **kwargs):
    await _janus_queue.async_q.put((func, args, kwargs))


# sync put new task to janus queue
def janus_queue_put_sync(_janus_queue: Queue, func: Callable, *args, **kwargs):
    _janus_queue.sync_q.put((func, args, kwargs))


def convert_file(input_path, target_format):
    """
    Reference: http://imageio.readthedocs.io/en/latest/examples.html#convert-a-movie
    :param input_path: full path for input file
    :param target_format: '.gif', '.avi' or '.mp4'
    """
    output_path = os.path.splitext(input_path)[0] + target_format
    logger.debug(f"converting {input_path} to {output_path}")

    reader = imageio.get_reader(input_path)
    fps = reader.get_meta_data()['fps']

    writer = imageio.get_writer(output_path, fps=fps)
    for i, im in enumerate(reader):
        sys.stdout.write("\rframe {0}".format(i))
        sys.stdout.flush()
        writer.append_data(im)
    logger.debug("\r\nFinalizing...")
    writer.close()
    logger.debug("Done.")


def convert_tgs_to_gif(tgs_file: str, gif_file: str) -> bool:
    """
    copied from EH Forwarder Bot
    :param tgs_file: full path
    :param gif_file: full output path
    :return:
    """
    # Import only upon calling the method due to added binary dependencies
    # (libcairo)
    from tgs.parsers.tgs import parse_tgs
    from tgs.exporters.gif import export_gif

    # noinspection PyBroadException
    try:
        animation = parse_tgs(tgs_file)
        # heavy_strip(animation)
        # heavy_strip(animation)
        # animation.tgs_sanitize()
        export_gif(animation, gif_file, skip_frames=1)
        return True
    except Exception:
        logger.exception("Error occurred while converting TGS to GIF.")
        return False


