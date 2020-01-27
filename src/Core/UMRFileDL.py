from typing import Dict
import aiohttp
from . import UMRConfig
from PIL import Image
from io import BytesIO
from . import UMRLogging
import os
from uuid import uuid4

download_dir = UMRConfig.config['DataRoot']

cache: Dict[str, str] = dict()  # Dict[url, file_name]

logger = UMRLogging.getLogger('FileDL')


async def get_image(url, file_id='', format='jpg'):
    """

    :param url: file url, cached for traffic saving
    :param file_id: unique file id, will replace cache index if specified (for dynamic urls)
    :param format: jpg, png or gif (currently not supported)
    :return:
    """
    if file_id:
        if file_id in cache:
            logger.debug(f'{file_id} found in cache')
            return cache[file_id]
        else:
            logger.debug(f'{file_id} not found in cache, downloading {format}')
    elif url in cache:
        logger.debug(f'{url} found in cache')
        return cache[url]
    else:
        logger.debug(f'{url} not found in cache, downloading {format}')
    async with aiohttp.ClientSession() as session:
        logger.debug('download started')
        async with session.get(url) as response:
            logger.debug('download finished')
            try:
                img: Image = Image.open(BytesIO(await response.read()))
                if format.lower().startswith('jpg') and img.mode != 'RGB':
                    img = img.convert('RGB')
            except OSError as e:
                logger.warning(f'Cannot convert {url}. It might be .tgs file which is not supported at this time.')
            file_name = str(uuid4()) + '.' + format
            file_full_path = os.path.join(download_dir, file_name)
            img.save(file_full_path)
            if file_id:
                cache[file_id] = file_full_path
                logger.debug(f'{file_id} download complete. Saved as {file_full_path}')
            else:
                cache[url] = file_full_path
                logger.debug(f'{url} download complete. Saved as {file_full_path}')
            return file_full_path


def empty_cache_dir():
    """
    run on start up
    :return:
    """
    file_list = [f for f in os.listdir(download_dir)]
    for f in file_list:
        os.remove(os.path.join(download_dir, f))
