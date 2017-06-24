# coolq-telegram-bot

QQ和Telegram的消息互转机器人

QQ部分基于[酷Q Socket API](https://github.com/yukixz/cqsocketapi)，Telegram部分基于[Telepot](https://github.com/nickoala/telepot)

源码基于[yukixz/qqbot.py](https://github.com/yukixz/qqbot.py)

# 功能和特性

+ 支持QQ群和Telegram群的文字消息互转
+ QQ群的图片可以发给Telegram群，Telegram群的图片将会以链接的形式发送到QQ群
+ Telegram群的Sticker会转换成对应的emoji发送给QQ群，QQ群的常用QQ表情会以emoji的形式发送到Telegram群
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


# Bot的运行

保证酷Q已启动并登录，使用`python3 awdbot.py`命令即可启动。
