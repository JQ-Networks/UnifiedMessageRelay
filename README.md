# coolq-telegram-bot

QQ和Telegram的消息互转机器人

QQ部分基于[酷Q Socket API](https://github.com/yukixz/cqsocketapi)，Telegram部分基于[Telepot](https://github.com/nickoala/telepot)

源码基于[yukixz/qqbot.py](https://github.com/yukixz/qqbot.py)

# 功能和特性

+ 支持QQ群和Telegram群的文字消息互转
+ QQ群的图片可以转发Telegram群，Telegram群的图片将会以链接的形式转发到QQ群
+ Telegram群的Sticker会转换成对应的emoji转发给QQ群，QQ群的常用QQ表情会以emoji的形式转发到Telegram群
+ 支持开启Telegram群的Sticker导出模式，开启该模式后，在QQ可以通过链接保存Sticker。
+ QQ群可以通过指令向Telegram群发送Sticker

# 环境的搭建

## Wine 酷Q

Wine 酷Q的安装可以参照[【简单教程】在 DigitalOcean 的 Ubuntu Server 下运行 酷Q Air](https://cqp.cc/t/30970)

用Docker也是可以的，可以参考[coolq/wine-coolq](https://hub.docker.com/r/coolq/wine-coolq/)，需要把酷Q Socket API用到的11235端口设置为外部可访问。

安装完之后，通过RDP的方式进入远程桌面，启动酷Q，输入QQ号和密码进行登录。Wine 酷Q不是特别稳定。如果在此过程中崩溃，请重新打开直至登陆成功。

## 安装酷Q Socket API

1. 在[酷Q Socket API的发布页](https://github.com/yukixz/cqsocketapi/releases)下载org.dazzyd.cqsocketapi.cpk文件
1. 将org.dazzyd.cqsocketapi.cpk文件放置到coolq/app下
1. 修改coolq/conf/CQP.cfg文件，在[App]项目中加入一行：org.dazzyd.cqsocketapi.status=1
1. 通过RDP的方式进入远程桌面，重启酷Q。在酷Q的插件管理界面中可以看到Socket API已启用。

## 开启图片静态资源访问

由于酷Q Air不支持往QQ群发送图片，所以Telegram群的图片将会以链接的形式发送到QQ群。此时需要将图片提供给外部访问。这里以nginx为例。

Ubuntu下安装nginx只需要用apt-get

`sudo apt-get install nginx`

修改nginx/conf/nginx.conf文件，以下配置即是将/home/coolq/coolq/data/image的内容映射到了jiagao.dynv6.net:8080/image

```
server {
    listen       8080;
    server_name  jiagao.dynv6.net;

    location /image/ {
        root /home/coolq/coolq/data;
    }
}
```

## 安装必须的python3包

`pip3 install urllib3 telepot pillow APScheduler requests requests-oauthlib`


# 参数和配置

## bot_constant.py

tgToken：Telegram机器人的token

tgBotId：Telegram机器人的ID

qqBotId：QQ机器人的QQ号

forwardIds：一个list，可以定义多个转发关系，list中的每一个tuple(QQ群的群号, Telegram群的群ID)都代表一个转发关系。仅支持QQ群和Telegram群一一对应的关系。

server_pic_url：图片访问的url前缀。

## special_sticker_list.py

specialStickerList：定义了`指令`和Telegram Sticker ID的对应。

在QQ群里输入`!指令`，即在Telegram群里发送一个对应的Sticker。

## qq_emoji_list.py

qqEmojiList：定义了QQ表情ID和emoji的对应。

这个列表实现了QQ表情和emoji的对应，可以根据需要进行修改。

## namelist.json

定义了QQ号和群昵称的对应。

由于Socket API无法获取成员列表，现阶段采用手动对应的形式。如果列表中没有定义某个QQ号对应的昵称，转发到Telegram群的消息发送者只能显示QQ号。

## admin.json

定义了管理员的QQ号。

// 其实这个bot里没用到这个。

# Bot的运行

保证酷Q已启动并登录，在bot_constant.py内填好了必需的参数，使用`python3 awdbot.py`命令即可启动。

# Sticker导出模式

开启：在QQ群或Telegram群中发送 [sticker link on]

关闭：在QQ群或Telegram群中发送 [sticker link off]

开启后，Sticker转发到QQ群的时候，会显示图片链接。

# 开车模式

开启：在QQ群或Telegram群中发送 [drive mode on]

关闭：在QQ群或Telegram群中发送 [drive mode off]

开启后，Telegram消息不会转发到QQ群内，QQ消息依然能转发到Telegram群组里。
