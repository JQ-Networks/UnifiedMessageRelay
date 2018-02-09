# -*- coding: utf-8 -*-
"""
该脚本可将配置文件bot_constant.py转换为bot_constant.json并保存在当前目录下。

[Useage]
python3 bot_constant-py2json.py [-i *.py file]
    -i 指定输入文件，如不指定则默认为../bot_constant.py
"""

import json
import os.path
import argparse


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
    return settings


if __name__ == '__main__':
    defFilePath = "../bot_constant.py"
    aP = argparse.ArgumentParser(
        description="该脚本可将配置文件bot_constant.py转换为bot_constant.json并保存在当前目录下。")
    aP.add_argument('-i', default=defFilePath, type=str,
                    help='指定输入文件，如不指定则默认为../bot_constant.py')
    filepath1 = vars(aP.parse_args())['i']
    # get vars
    if filepath1 == defFilePath:
        with open(os.path.abspath(defFilePath), mode='r', encoding="UTF-8") as f1:
            ex = f1.read()
        exec(ex)
    else:
        with open(filepath1, mode='r', encoding="UTF-8") as f1:
            ex = f1.read()
        exec(ex)
    # get JSON
    text = json.dumps(get_global_settings(), sort_keys=False, indent=4)
    with open('bot_constant.json', 'w') as fo:
        fo.write(text)
    print(text)
