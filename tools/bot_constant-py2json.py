"""
该脚本可将配置文件bot_constant.py转换为bot_constant.json并保存在当前目录下。

[Useage]
python3 bot_constant-py2json.py [-i *.py file]
    -i 指定输入文件，如不指定则默认为../bot_constant.py
"""

import sys
import json
import os.path


def py2json():
    r = {}
    r.setdefault("TOKEN", TOKEN)
    r.setdefault('QQ_BOT_ID', QQ_BOT_ID)

    # cq-http-api server config
    r.setdefault("API_ROOT", API_ROOT)
    r.setdefault("ACCESS_TOKEN", ACCESS_TOKEN)
    r.setdefault("SECRET", ACCESS_TOKEN)
    # cq-http-api client config
    r.setdefault("HOST", ACCESS_TOKEN)
    r.setdefault("PORT", ACCESS_TOKEN)

    r.setdefault('FORWARD_LIST', FORWARD_LIST)
    r.setdefault('SERVER_PIC_URL', SERVER_PIC_URL)
    r.setdefault('CQ_ROOT', CQ_ROOT)
    r.setdefault('CQ_PORT', CQ_PORT)
    r.setdefault('JQ_MODE', JQ_MODE)
    jData = json.dumps(r, indent=4)
    print(jData)
    return jData


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
    with open('bot_constant.json', 'w') as fo:
        fo.write(py2json())
