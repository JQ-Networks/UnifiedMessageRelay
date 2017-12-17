"""
该脚本可将配置文件bot_constant.py转换为bot_constant.json并保存在当前目录下。

[Useage]
python3 bot_constant-py2json.py [-i *.py file]
    -i 指定输入文件，如不指定则默认为../bot_constant.py
"""

import sys
import json
import os.path


def get_global_settings():
    """
    Convert global var into dict
    return a dict
    """
    settings = {}
    settings.setdefault('DEBUG_MODE', DEBUG_MODE)
    settings.setdefault('BAIDU_API', BAIDU_API)
    settings.setdefault('API_ROOT', API_ROOT)
    settings.setdefault('ACCESS_TOKEN', ACCESS_TOKEN)
    settings.setdefault('SECRET', SECRET)
    settings.setdefault('HOST', HOST)
    settings.setdefault('PORT', PORT)
    settings.setdefault('TOKEN', TOKEN)
    settings.setdefault('QQ_BOT_ID', QQ_BOT_ID)
    settings.setdefault('FORWARD_LIST', FORWARD_LIST)
    settings.setdefault('SERVER_PIC_URL', SERVER_PIC_URL)
    settings.setdefault('CQ_ROOT', CQ_ROOT)
    settings.setdefault('JQ_MODE', JQ_MODE)
    return settings


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '-i':
        filepath1 = sys.argv[2]
        with open(filepath1, mode='r') as f1:
            ex = f1.read()
        exec(ex)
    elif len(sys.argv) == 1:
        with open(os.path.abspath('../bot_constant.py'), mode='r') as f1:
            ex = f1.read()
        exec(ex)
    else:
        print(__doc__)
        exit(1)
    text = json.dumps(get_global_settings(), sort_keys=False, indent=4)
    with open('bot_constant.json', 'w') as fo:
        fo.write(text)
    print(text)
