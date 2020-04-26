# UnifiedMessageRelay

![shields](https://img.shields.io/badge/python-3.7%2B-blue.svg?style=flat-square) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Telegram support group](https://img.shields.io/badge/support-telegram-blue)](https://t.me/s/UnifiedMessageRelay)
[![Telegram developer group](https://img.shields.io/badge/developer-telegram-blue)](https://t.me/s/UnifiedMessageRelayDev)

UnifiedMessageRelay is a framework for the purpose of bringing messages from different chat platform together. With UnifiedMessageRelay,
user no longer need to view messages on different platform, or different groups. UnifiedMessageRelay brings powerful
 message forwarding functionality and flexible plugin API to meet your custom need. A driver API specification is also
 provided, so one can compose their own backend driver, and the framework will load and utilize the driver automatically.


## Demo

Telegram <-> QQ:

<img src="image/telegram.png" height="400" alt="Telegram">

<img src="image/qq.png" height="600" alt="QQ">

Telegram <-> Discord:

<img src="image/tg-discord1.png" height="500" alt="Discord">

<img src="image/tg-discord2.png" height="500" alt="Telegram">

All four platforms: QQ, Telegram, Line and Discord can forward between each other directly.

## Supported platforms

- QQ API based on [CoolQ HTTP API](https://github.com/richardchien/coolq-http-api) [aiocqhttp](https://github.com/cqmoe/python-aiocqhttp)
- Mirai API based on multiple repos from [Mamoe Technologies](https://github.com/mamoe)
- Telegram API based on [aiogram](https://aiogram.dev)
- Line API based on [linebotx](https://github.com/Shivelight/line-bot-sdk-python-extra) [linebot](https://github.com/line/line-bot-sdk-python)
- Discord API based on [Discord.py](https://github.com/Rapptz/discord.py)

## Update

[ChangeLog.md](ChangeLog.md)

## Features

- Forward text and image between all supported platforms
- Image is converted to supported format automatically
- Reply is preserved with best effort
- Markdown format is preserved for supported platforms
- Command API for customize triggers
- Message Hook API for even more customized needs

Limited support for Coolq Air. image sending is available for Coolq Pro.

## Installation

### Framework Setup
### Install python dependencies on host os

Make sure Python 3.7+ and `pip` are installed. Run:

`pip3 install unified-message-relay`

### TLDR

To install every python module in one line:

`pip3 install -U umr_telegram_driver umr_line_driver umr_discord_driver umr_coolq_driver umr_mirai_driver umr_extensions_demo`

### Install other required package on host os

`apt install libcairo2 ffmpeg libmagickwand-dev`

## Configurations

Create `~/.umr/`

```bash
mkdir ~/.umr
```

Copy config.yaml to `~/.umr`

[Why yaml instead of json?](https://www.quora.com/What-situation-would-you-use-YAML-instead-of-JSON-or-XML)

[Full Example config](config.yaml)

The "QQ", "Telegram" or "Line" above are all custom names. Real bot driver should be configure throgh "Driver" list.

### Follow the guide for your platform

[QQ](Installation/QQ.md)

[Mirai](Installation/Mirai.md)

[Telegram](Installation/Telegram.md)

[Line](Installation/Line.md)

[Discord](Installation/Discord.md)

## Start the bot

### Viewing CLI Help

```shell
unified-message-relay -h
```

### Background process

- Start background service

```shell
unified-message-relay start
```

or

```shell
unified-message-relay restart
```

By default, log will be stored in `/var/log/umr/bot.log`, and cache will be cleared out upon start.

- Stop the background service

```shell
unified-message-relay stop
```

### Foreground process (for debugging purpose)

If you need to see the log output for debugging purpose, stop the running daemon first. Then follow this command.

Remember to enable debug option in config.

```shell
unified-message-relay run
```

Hit Ctrl + C to stop.

## Extensions and Commands

Example extensions and commands now require extension `umr-extensions-demo`:

```bash
pip install umr-extensions-demo
```

and put `- umr_extensions_demo` under `Extensions` section of `config.yaml`.

### Available commands
#### Help

Send `!!help` to show available commands.

This command requires no extra module. 

#### Show chat id

Send `!!id` anywhere to see chat id.

Reply message with `!!id` to reveal source chat id.

This command requires `cmd_id.py` under umr_extension_demo. 

#### Delete QQ Message

Reply to the message you want to delete with `!!del`

This command requires `QQ_recall.py` under umr_extension_demo and using coolq driver. 
Mirai recall is not supported at this time. 

#### Add telegram blocked keyword

Message containing these keyword will not be forwarded to any other chat

Send `!!bk` and keywords separated by space

This command requires `Telegram_watermeter.py` under umr_extension_demo and using telegram driver.

#### Add telegram blocked channel

Message originated from these channel will not be forwarded to any other chat

Reply forwarded channel message with `!!bc`

This command requires `Telegram_watermeter.py` under umr_extension_demo and using telegram driver.

To modify saved keywords and channels, edit `ExtensionConfig` section in `config.yaml`.

### Available Extensions

#### Comment filter

Add `//` at the beginning of the message to avoid forwarding to any other chat.

# Issue Format

## Check these before opening an issue

1. Use `unified-message-relay run` to print log to stdout
2. Check if you are using Python 3.7+
3. Check if binary dependencies are installed (search apt in this page)
4. (If using Coolq) Check if cq-http-api is enabled in Coolq
5. Check if the log suggests any missing configuration
6. Check if you are on Dev branch, please switch back to master (dev may be unstable)

## Issues must provide

1. Descriptions about the issue
2. Logs of python3 daemon.py run (Desensitization)
3. Steps to reproduce

