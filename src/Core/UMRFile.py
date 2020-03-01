from typing import Dict
import aiohttp
from . import UMRConfig
from PIL import Image
from io import BytesIO
from . import UMRLogging
import os
from uuid import uuid4
import filetype
from tgs.parsers.tgs import parse_tgs
from tgs.exporters.gif import export_gif
import ffmpy
from wand.image import Image as WandImage

download_dir = UMRConfig.config['DataRoot']

cache: Dict[str, str] = dict()  # Dict[url, file_name]

logger = UMRLogging.get_logger('FileDL')

# By default, a image downgrading mapping is hardcoded here
# If more platform is being added, might need to add more conversion mapping
default_target_format = {
    'image/jpeg':       'image/jpeg',
    'image/jpx':        'image/jpeg',
    'image/png':        'image/png',
    'image/gif':        'image/gif',
    'image/webp':       'image/png',
    'image/tiff':       'image/jpeg',
    'image/bmp':        'image/bmp',
    'image/heic':       'image/jpeg',

    'video/mp4':        'image/gif',
    'video/webm':       'image/gif',
    'application/gzip': 'image/gif'  # telegram .tgs sticker

}

mime_to_extension = {
    'image/jpeg': '.jpg',
    'image/png':  '.png',
    'image/gif':  '.gif',
    'image/bmp':  '.bmp',

}


async def get_image(url, file_id='', target_format=''):
    """

    :param url: file url, cached for traffic saving
    :param file_id: unique file id, will replace cache index if specified (for dynamic urls)
    :param target_format: override the default target_format
    :return:
    """
    try:
        if file_id:
            if file_id in cache:
                logger.debug(f'{file_id} found in cache')
                return cache[file_id]
            else:
                logger.debug(f'{file_id} not found in cache, downloading...')
        elif url in cache:
            logger.debug(f'{url} found in cache')
            return cache[url]
        else:
            logger.debug(f'{url} not found in cache, downloading...')
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                logger.debug('download finished')
                image = BytesIO(await response.read())
                try:
                    file_mime = filetype.guess_mime(image)
                except TypeError:
                    logger.exception('Unrecognized image format')
                    return ''
                if not file_mime:
                    logger.debug(f'filetype did not recognize this format')
                    return ''
                if file_mime not in default_target_format:
                    logger.error(f'{file_mime} is not supported at this time')

                image.seek(0)  # restart from head
                target_file_name = str(uuid4()) + mime_to_extension[default_target_format[file_mime]]
                file_full_path = os.path.join(download_dir, target_file_name)

                if file_mime == 'application/gzip':  # tgs file
                    convert_tgs_to_gif(image, file_full_path)
                elif file_mime == 'video/mp4' or file_mime == 'video/webm':  # tg animation
                    convert_mp4_to_gif(image, file_full_path)
                elif file_mime == 'image/webp':
                    convert_webp_to_png(image, file_full_path)
                elif default_target_format[file_mime] == file_mime:
                    open(file_full_path, 'wb').write(image.read())
                else:
                    img = Image.open(image)
                    img = img.convert('RGB')
                    img.save(file_full_path)

                if file_id:
                    cache[file_id] = file_full_path
                    logger.debug(f'{file_id} download complete. Saved as {file_full_path}')
                else:
                    cache[url] = file_full_path
                    logger.debug(f'{url} download complete. Saved as {file_full_path}')
                return file_full_path
    except:
        logger.exception('Unhandled exception, download aborted')
        return ''


def convert_mp4_to_gif(mp4_file: [str, BytesIO], gif_file: str):
    """
    Reference: http://imageio.readthedocs.io/en/latest/examples.html#convert-a-movie
    :param mp4_file: full path or BytesIO object
    :param gif_file: full output path
    """
    if isinstance(mp4_file, str):
        input_file = mp4_file
    else:
        input_file = '/tmp/' + str(uuid4()) + '.mp4'
        f = open(input_file, 'wb')
        f.write(mp4_file.read())
        f.close()

    tmp_palettegen_path = '/tmp/' + str(uuid4()) + '.png'

    ff = ffmpy.FFmpeg(inputs={input_file: None},
                      outputs={tmp_palettegen_path: '-vf palettegen'},
                      global_options=('-y'))
    ff.run()
    ff = ffmpy.FFmpeg(inputs={input_file: None, tmp_palettegen_path: None},
                      outputs={gif_file: '-filter_complex paletteuse'},
                      global_options=('-y'))
    ff.run()
    os.remove(input_file)
    os.remove(tmp_palettegen_path)


def convert_tgs_to_gif(tgs_file: [str, BytesIO], gif_file: str) -> bool:
    """
    copied from EH Forwarder Bot
    :param tgs_file: full path or BytesIO
    :param gif_file: full output path
    :return:
    """
    # require (libcairo2)

    logger.debug(f"converting tgs to {gif_file}")
    # noinspection PyBroadException
    try:
        animation = parse_tgs(tgs_file)
        export_gif(animation, gif_file, skip_frames=5, dpi=48)
        return True
    except Exception:
        logger.exception("Error occurred while converting TGS to GIF.")
        return False


def convert_webp_to_png(webp_file: [str, BytesIO], png_file: str) -> bool:
    """
    copied from EH Forwarder Bot
    :param webp_file: full path or BytesIO
    :param png_file: full output path
    :return:
    """
    if isinstance(webp_file, str):
        input_file = webp_file
    else:
        input_file = '/tmp/' + str(uuid4()) + '.webp'
        f = open(input_file, 'wb')
        f.write(webp_file.read())
        f.close()

    logger.debug(f"converting webp to {png_file}")

    img = WandImage(filename=input_file)
    img.save(filename=png_file)

    os.remove(input_file)


def empty_cache_dir():
    """
    run on start up
    :return:
    """
    file_list = [f for f in os.listdir(download_dir)]
    for f in file_list:
        os.remove(os.path.join(download_dir, f))


empty_cache_dir()
