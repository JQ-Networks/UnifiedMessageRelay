# coolq-telegram-bot 
![](https://img.shields.io/badge/python-3.6%2B-blue.svg?style=flat-square) ![](https://img.shields.io/badge/license-GPLv3-000000.svg?style=flat-square)

## Demo
Telegram:

![Telegram](https://github.com/jqqqqqqqqqq/coolq-telegram-bot/raw/master/image/telegram.png)

QQ:

![QQ](https://github.com/jqqqqqqqqqq/coolq-telegram-bot/raw/master/image/qq.png)

[中文 Readme](https://github.com/jqqqqqqqqqq/coolq-telegram-bot/blob/master/README-zh_CN.md)

## Description
QQ & Telegram Relay Bot **v3.1**

QQ API based on [CoolQ HTTP API](https://github.com/richardchien/coolq-http-api)，Telegram API based on [python_telegram_bot](https://python-telegram-bot.org)

## Recent Update
### v3.1
- Support Message Recalling（2-minute limitation）
- Edits will recall old messages（2-minute limitation）

[View More](https://github.com/jqqqqqqqqqq/coolq-telegram-bot/ChangeLog.md)

----------------------------

## Docker Usage

1. Star This Repo
2. Star [This](https://github.com/Z4HD/coolq-telegram-bot-docker) repo
3. Follow coolq-telegram-bot-docker's [Readme](https://github.com/Z4HD/coolq-telegram-bot-docker/blob/master/README.md)


## Features

### If you are using CoolQ Air

+ Support text forward between QQ and Telegram
+ Images from QQ will be forwarded to Telegram, but Telegram images will be forwarded via links
+ Telegram stickers will be converted to emojis, with link if enabled IMAGE_LINK_MODE
+ Some QQ emojis will be converted to unicode emojis 
+ Support temporarily disable forwarding
+ Support commands, use `!!show commands` or `!!cmd` to list

### If you are using CoolQ Pro

+ Support text forward between QQ and Telegram
+ Images will be forwarded to opposite sides
+ Some QQ emojis will be converted to unicode emojis 
+ Support commands, use `!!show commands` or `!!cmd` to list

## Build Environment

### Use Docker
Docker is preferred, choose one from below if you want

- [coolq/wine-coolq](https://hub.docker.com/r/coolq/wine-coolq/)  *Official Coolq Docker*
- [richardchien/cqhttp](https://richardchien.github.io/coolq-http-api/3.3/#/Docker) *richardchien's Coolq Docker, with Coolq http api*
- [coolq-telegram-bot-docker](https://github.com/Z4HD/coolq-telegram-bot-docker) *Based on richardchien's Coolq Docker, with Coolq Telegram Bot* <b>require manually `build` </b>。

Please follow the instruction of the one you chose, and jump to **Configuration** part of this instruction


### Directly use Wine CoolQ
If you don't prefer Docker, follow this instruction (Please use Ubuntu, since bugs appear on Debian 9)
> [【简单教程】在 DigitalOcean 的 Ubuntu Server 下运行 酷Q Air](https://cqp.cc/t/30970)

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
update_source=https://raw.githubusercontent.com/richardchien/coolq-http-api-release/master/
update_channel=stable
auto_check_update=no
auto_perform_update=no
thread_pool_size=4
server_thread_pool_size=1
```

### Enable static image server (Coolq Air Only)

Since Coolq Air doesn't support sending images, Telegram images will be sent via link. You need to expose these images for access.

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

### install python dependencies

`pip3.6 install -r requirements.txt`

## Configurations

### bot_constant.py

Please rename `bot_constant-sample.py` to `bot_constant.py` before use.

Key              | Value
:--------------- | ---
`TOKEN`          | Telegram tot token
`QQ_BOT_ID`      | QQ bot number
`FORWARD_LIST`   | A list that defines forwards. Every dict in this list `[QQ Group Number, Telegran Group ID，Default for DRIVE_MODE, Default for IMAGE_LINK_MODE]` stands for a forward. Only one to one forward is supported.
`SERVER_PIC_URL` | Your server's domain(used for url access, if you are using Pro, you can set whatever you like since it is not used)
`CQ_ROOT_DIR`    | Coolq's root directory
`API_ROOT`       | 'http://127.0.0.1:5700/' cq-http-api's api root
`ACCESS_TOKEN`   | 'access_token'   cq-http-api's access_token, see cq-http-api's doc for further information
`SECRET`         | 'secret '  cq-http-api's secret, see cq-http-api's doc for further information
`HOST`           | '127.0.0.1' cq-http-api's event report address
`PORT`           | 8080 cq-http-api's event report port
`DEBUG_MODE`     | Debug mode. Set to True is encouraged. Since rotate log handler is used, it will take up no more than 3MB.


### bot_constant.json
Key - Value peer is the same as above

If you want to use JSON, please copy `bot_constant-json.py` to `bot_constant.py`

if you want to load external settings file, use `CTB_JSON_SETTINGS_PATH`

Example:

```shell
$ export CTB_JSON_SETTINGS_PATH="/home/user/bot_constant.json"
```
`tools/bot_constant-py2json.py` provides  convertion from `bot_constant.py` tp `bot_constant.json`

## deploy bot

1. clone this git to docker's data folder (google about where it is)
2. use `sudo docker exec -it coolq su` to launch docker shell
3. then you'll be able to find out the bot under `/home/user/coolq`

## Start bot

Attention: Python 3.6 is required due to variable type hinting is used

Make sure Coolq is started and logged in, bot_constant.py is configured

Use `python3.6 daemon.py run` to start your bot. This will run your bot in foreground and enable DEBUG mode temporarily

If no ERROR occurs, please `Ctrl C` and use `python3.6 daemon.py start`

There're other commands like `stop` and `restart`

When updating bot, be aware of that `restart` sometimes cause error. Please `stop` and `start` instead.

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

Forward function will be disabled temporarily after enabled this

### Recall（v3.1+）

Reply `!!recall` or `!!del` in Telegram to any message you want to recall in QQ.

Message must be sent by bot in QQ side.

** If the message exceed 2 minutes, recall will fail**

# Management Features (Under Construction)

Currently QQ group invites and accept invites is available via private chat.

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



