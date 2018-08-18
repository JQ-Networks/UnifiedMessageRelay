# coolq-telegram-bot 
![](https://img.shields.io/badge/python-3.6%2B-blue.svg?style=flat-square) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

Alternative Project: [coolq-telegram-bot-x](https://github.com/JogleLew/coolq-telegram-bot-x)

coolq-telegram-bot-x is written in C++ and is still under construction, but it needs no Python environment at all. The difference is that **THIS REPO** is on the fast ring, and it intends for feature developments, and **coolq-telegram-bot-x** intends for higher performance, but until now it has fewer features.

## Demo
Telegram:

![Telegram](https://github.com/jqqqqqqqqqq/coolq-telegram-bot/raw/master/image/telegram.png)

QQ:

![QQ](https://github.com/jqqqqqqqqqq/coolq-telegram-bot/raw/master/image/qq.png)

》》[中文 Readme](README-zh_CN.md)《《

QQ & Telegram Relay Bot **v3.4**
€
QQ API based on [CoolQ HTTP API](https://github.com/richardchien/coolq-http-api)，Telegram API based on [python_telegram_bot](https://python-telegram-bot.org)

## Recent Update

## v3.4.1

- Fix Stickers forward issue
- Dockerfile: add libwebp

## v3.4

- *** License changed to MIT ***
- Dockerfile：use Alpine image
- Dockerfile：fixed ffmpeg installation
- Cache Management(partial)：use MD5 to identify file，send fileid instead of whole file
- Code classification, optimization for recall and “//”
- keyword filter changed to not forwarding single message, instead of enabling drive mode
- drive mode now modifies title of groups

[View More](ChangeLog.md)*(Chinese)*

----------------------------

## Features

### If you are using CoolQ Air

+ Support text forward between QQ and Telegram
+ Images from QQ will be forwarded to Telegram, but Telegram images will be forwarded via links
+ Telegram stickers will be converted to emojis, with the link if enabled IMAGE_LINK_MODE
+ Some QQ emojis will be converted to Unicode emojis 
+ Support temporarily disable forwarding
+ Support commands, use `!!show commands` or `!!cmd` to list

### If you are using CoolQ Pro

+ Support text forward between QQ and Telegram
+ Images will be forwarded to opposite sides
+ Some QQ emojis will be converted to Unicode emojis 
+ Support commands, use `!!show commands` or `!!cmd` to list

## Build Environment

### Use Docker

Now support docker-compose, [more details](docker-compose-zh_CN.md) *(Chinese)*

Only want to run Coolq in a container? These images below here may useful.

- [coolq/wine-coolq](https://hub.docker.com/r/coolq/wine-coolq/)  *Official Coolq Docker*
- [richardchien/cqhttp](https://richardchien.github.io/coolq-http-api/3.3/#/Docker) *richardchien's Coolq Docker, with Coolq http api*

Please follow the instruction of the one you chose, and jump to [**Configuration**](#configurations) part of this instruction


### Directly use Wine CoolQ
If you don't prefer Docker, follow this instruction (Please use Ubuntu, since bugs appear on Debian 9)
> [【简单教程】在 DigitalOcean 的 Ubuntu Server 下运行 酷Q Air](https://cqp.cc/t/30970)
apt-get install libcurl4-openssl-dev libssl-dev ffmpeg

### Install CoolQ HTTP API
> See [CoolQ HTTP API Documentary](https://richardchien.github.io/coolq-http-api/3.3/#/)

- Typical Coolq http api config (`app/io.github.richardchien.coolqhttpapi/config.cfg`)

```
[general]
host=0.0.0.0
port=5700
use_http=yes
ws_host=0.0.0.0
ws_port=5700
use_ws=no
post_url=http://127.0.0.1:8080
access_token=very
secret=long
post_message_format=array
serve_data_files=no
update_channel=stable
auto_check_update=no
auto_perform_update=no
```

### Enable static image server (Coolq Air Only)

Since Coolq Air doesn't support sending images, Telegram images will be sent via the link. You need to expose these images for access.

Install nginx under Ubuntu

 `sudo apt-get install nginx`

edit nginx/conf/nginx.conf，this config maps `/home/coolq/coolq/data/image` to `www.example.com:8080/image`

```
server {
    listen 8080;
    server_name www.example.com; 
    location /image/ { 
        root /home/coolq/coolq/data; 
    } 
} 
```

### Install python dependencies

`pip3.6 install -r requirements.txt`

## Configurations

Key              | Value
:--------------- | ---
`TOKEN`          | Telegram tot token
`QQ_BOT_ID`      | QQ bot number
`FORWARD_LIST`   | A list that defines forwards. Every dict in this list `[QQ Group Number, Telegran Group ID，Default for DRIVE_MODE, Default for IMAGE_LINK_MODE]` stands for a forward. Only one to one forward is supported.
`SERVER_PIC_URL` | Your server's domain(used for url access, if you are using Pro, you can set whatever you like since it is not used)
`CQ_ROOT_DIR`    | Coolq's root directory
`API_ROOT`       | 'http://127.0.0.1:5700/' cq-http-api's API root
`ACCESS_TOKEN`   | 'access_token'   cq-http-api's access_token, see cq-http-api's doc for further information
`SECRET`         | 'secret '  cq-http-api's secret, see cq-http-api's doc for further information
`HOST`           | '127.0.0.1' cq-http-api's event report address
`PORT`           | 8080 cq-http-api's event report port
`DEBUG_MODE`     | Debug mode. Set to True is encouraged. Since rotate log handler is used, it will take up no more than 3MB.
 `PROXY_URL` | Connects to the specified Socks5 proxy address and does not use proxy when the value is *empty* or `False`.<br />*(optional in JSON, the default is `None`)*
 `USE_SHORT_URL` | Use short links, it is recommended to open.<br />*(optional in JSON, the default is `true`)*

### bot_constant.py

Please rename `bot_constant-sample.py` to `bot_constant.py` before use.

### bot_constant.json
Key - Value peer is the same as above

If you want to use JSON, please copy or soft-link `bot_constant-json.py` to `bot_constant.py`

```bash
$ ln -s bot_constant-json.py bot_constant.py
```

if you want to load external settings file, use `CTB_JSON_SETTINGS_PATH`

Example:

```shell
$ export CTB_JSON_SETTINGS_PATH="/home/user/bot_constant.json"
```
`tools/bot_constant-py2json.py` provides  convertion from `bot_constant.py` to `bot_constant.json`

## Start the bot

Make sure that you have finished all configure steps.

### Viewing CLI Help

```shell
$ python3.6 daemon.py -h
```

### Background process

Currently daemon mode has been implemented, using the following instructions to run in the background.

- Start background service

```shell
$ python3.6 daemon.py start
```

- Stop the background service

```shell
$ python3.6 daemon.py stop
```

### Front desk process

If you need to see the log output in real time, close the running daemon first. Then follow this command.

```shell
$ python3.6 daemon.py run
```

## Commands

### View Commands

Send `!!show commands` or `!!cmd` to view all commands

### View alipay red pack

Send `!!alipay` of `!!ali`，to acquire. This action will donate the author without costing your money

### Show Telegram Group ID

Send `!!show group id` or `!!id ` in Telegram groups to view Telegram Group ID

### Update QQ name list

Send `!!update namelist` or `!!name` to update qq name list manually

### Image Link Mode （Coolq Air Only）

Enable: Send `!!pic link on` or `!!lnkon`

Disable: Send `!!pic link off` or `!!lnkoff`

Telegram images and stickers will forward to QQ via links after enabled this

### Drive Mode

Enable：Send `!!drive mode on` or `!!drive`

Disable：Send `!!drive mode off` or `!!park`

The forward function will be disabled temporarily after enabled this

### Recall（v3.1+）

Reply `!!recall` or `!!del` in Telegram to any message you want to recall in QQ.

The message must be sent by the bot in QQ side.

** If the message exceeds 2 minutes, the recall will fail**

# Management Features (Under Construction)

Currently, QQ group invites and accept invites is available via private chat.

You can find out the usage by reading `plugins/_00x_xxxxx.py`

# Issue Format

## Check these before opening an issue

1. Check if you are using Python 3.6+
2. Check if requirements.txt is installed correctly
3. Check if cq-http-api is enabled in Coolq


## Issues must provide

1. Descriptions about the issue
2. Logs of python3 daemon.py run (Desensitization)
3. Whether you are using Docker
4. Which branch you are on (Dev of Master)
