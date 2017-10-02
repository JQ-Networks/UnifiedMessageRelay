# coolq-telegram-bot 

QQ和Telegram的消息互转机器人

2.0 版本正在构建中，预计有生之年

QQ部分基于[酷Q Socket API](https://github.com/yukixz/cqsocketapi)，Telegram部分基于[python_telegram_bot](https://python-telegram-bot.org)

源码基础为[yukixz/qqbot.py](https://github.com/yukixz/qqbot.py)

Coolq 群名片功能基础为[慕晓飞/cq_python_sdk](https://gitee.com/muxiaofei/cq_python_sdk/tree/master)

## 功能和特性

### 如果您使用的是酷Q Air

+ 支持QQ群和Telegram群的文字消息互转 
+ QQ群的图片可以转发Telegram群，Telegram群的图片将会以链接的形式转发到QQ群
+ Telegram群的Sticker会转换成对应的emoji转发给QQ群，QQ群的常用QQ表情会以emoji的形式转发到Telegram群 
+ 支持开启Telegram群的Sticker导出模式，开启该模式后，在QQ可以通过链接保存Sticker。
+ QQ群可以通过指令向Telegram群发送Sticker
+ 支持临时关闭Telegram群到QQ群的转发

### 如果您使用的是酷Q Pro

+ 支持QQ群和Telegram群的文字消息互转
+ QQ群的图片可以转发Telegram群，Telegram群的图片和sticker可以转发到QQ群，QQ群的QQ表情会以emoji的形式转发到Telegram群
+ QQ群可以通过指令向Telegram群发送Sticker
+ 支持临时关闭Telegram群到QQ群的转发

## 环境的搭建

### Wine 酷Q

推荐使用Docker镜像，可以参考[coolq/wine-coolq](https://hub.docker.com/r/coolq/wine-coolq/)，因为酷Q Socket API用到了一个数据监听端口，默认为11235端口，为方便起见，建议在容器内部运行本bot。

如果不使用Docker，Wine 酷Q的安装可以参照[【简单教程】在 DigitalOcean 的 Ubuntu Server 下运行 酷Q Air](https://cqp.cc/t/30970)

### 安装酷Q Socket API

1. 由于酷Q Socket API的发布页发布的版本较旧，请使用本仓库提供编译的最新版的Socket API，[点击这里](https://github.com/jqqqqqqqqqq/coolq-telegram-bot/releases)下载org.dazzyd.cqsocketapi.cpk文件。
1. 将org.dazzyd.cqsocketapi.cpk文件放置到coolq/app下 
1. 修改coolq/conf/CQP.cfg文件，在[App]项目中加入一行：org.dazzyd.cqsocketapi.status=1 
1. 通过远程连接进入远程桌面，重启酷Q。在酷Q的插件管理界面中可以看到Socket API已启用。 

### 开启图片静态资源访问

由于酷Q Air不支持往QQ群发送图片，所以Telegram群的图片将会以链接的形式发送到QQ群。此时需要将图片提供给外部访问。酷Q Pro也小概率会出现图片无法从QQ群转发到Telegram群的问题，所以也建议开启图片静态资源访问。这里以nginx为例。

Ubuntu下安装nginx只需要用

 `sudo apt-get install nginx`

修改nginx/conf/nginx.conf文件，以下配置即是将/home/coolq/coolq/data/image的内容映射到了www.example.com:8080/image

```
server {
    listen 8080;
    server_name www.example.com; 
    location /image/ { 
        root /home/coolq/coolq/data; 
    } 
} 
```

### 安装必须的python3包 

`pip3 install urllib3 python_telegram_bot pillow APScheduler requests requests-oauthlib`

## 参数和配置

### bot_constant.py

提示：请在bot使用之前，将bot_constant-sample.py重命名为bot_constant.py

TOKEN：Telegram机器人的token

QQ_BOT_ID：QQ机器人的QQ号

FORWARD_LIST：一个list，可以定义多个转发关系，list中的每一个list [QQ群的群号, Telegram群的群ID，图片链接模式默认值，开车模式默认值]都代表一个转发关系。仅支持QQ群和Telegram群一一对应的关系。

SERVER_PIC_URL：图片访问的url前缀。

CQ_ROOT_DIR：酷Q的根目录路径

CQ_PORT：酷Q Socket API 数据监听端口

JQ_MODE：交钱模式。如果使用酷Q Pro，请设置为True，如果使用酷Q Air，请设置为False。

### special_sticker_list.py

special_sticker_list：定义了`指令`和Telegram Sticker ID的对应。

在QQ群里输入`!指令`，即在Telegram群里发送一个对应的Sticker。

### qq_emoji_list.py

qq_emoji_list：定义了QQ表情ID和emoji的对应。

这个列表实现了QQ表情和emoji的对应，可以根据需要进行修改。列表中没有定义的QQ表情发送到Telegram群中会显示为问号。

## Bot的运行

保证酷Q已启动并登录，在bot_constant.py内填好了必需的参数，sample文件已经改名，使用`python3 mybot.py`命令即可启动。

## Sticker导出模式 

*此功能仅针对酷Q Air有效

开启：在QQ群或Telegram群中发送 [sticker link on]

关闭：在QQ群或Telegram群中发送 [sticker link off]

开启后，Sticker转发到QQ群的时候，会显示图片链接。

## 开车模式

开启：在QQ群或Telegram群中发送 [drive mode on]

关闭：在QQ群或Telegram群中发送 [drive mode off]

开启后，Telegram消息不会转发到QQ群内，QQ消息依然能转发到Telegram群组里。
