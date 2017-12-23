# coolq-telegram-bot 
![](https://img.shields.io/badge/python-3.6%2B-blue.svg?style=flat-square) ![](https://img.shields.io/badge/license-GPLv3-000000.svg?style=flat-square)

QQ和Telegram的消息互转机器人 **v3.1**

QQ部分基于[酷Q HTTP API](https://github.com/richardchien/coolq-http-api)，Telegram部分基于[python_telegram_bot](https://python-telegram-bot.org)

## 最近更新
### v3.1
- 支持撤回已发送消息（2分钟内）
- 支持编辑消息时撤回老消息（2分钟内）

查看更多

----------------------------

## docker 容器

1. Star 本 Repo
2. Star [这个](https://github.com/Z4HD/coolq-telegram-bot-docker) repo
3. 参考 coolq-telegram-bot-docker 的 [Readme](https://github.com/Z4HD/coolq-telegram-bot-docker/blob/master/README.md) 完成构建。


## 功能和特性

### 如果您使用的是酷Q Air

+ 支持QQ群和Telegram群的文字消息互转 
+ QQ群的图片可以转发Telegram群，Telegram群的图片将会以链接的形式转发到QQ群
+ Telegram群的Sticker会转换成对应的emoji转发给QQ群，QQ群的常用QQ表情会以emoji的形式转发到Telegram群 
+ 支持开启Telegram群的Sticker导出模式，开启该模式后，在QQ可以通过链接保存Sticker。
+ 支持命令，使用 !!show commands 或者 !!cmd 查看

### 如果您使用的是酷Q Pro

+ 支持QQ群和Telegram群的文字消息互转
+ QQ群的图片可以转发Telegram群，Telegram群的图片和sticker可以转发到QQ群，QQ群的QQ表情会以emoji的形式转发到Telegram群
+ 支持临时关闭转发
+ 支持命令，使用 !!show commands 或者 !!cmd 查看

## 环境的搭建

### 使用Docker部署
推荐使用Docker镜像部署酷Q

- [coolq/wine-coolq](https://hub.docker.com/r/coolq/wine-coolq/)  *酷Q官方镜像*
- [richardchien/cqhttp](https://richardchien.github.io/coolq-http-api/3.3/#/Docker) *基于wine-coolq的第三方镜像，内置了酷Q HTTP API*
- [coolq-telegram-bot-docker](https://github.com/Z4HD/coolq-telegram-bot-docker) *基于richardchien/cqhttp的镜像，内置了本Bot及其运行环境。* <b>需要手动 `build` </b>。

使用 Docker 部署后续请参考 Docker 版教程，本教程可以直接跳到 **参数和配置**

### 直接部署Wine 酷Q
如果不使用Docker，Wine 酷Q的安装可以参照酷Q论坛的教程。
> [【简单教程】在 DigitalOcean 的 Ubuntu Server 下运行 酷Q Air](https://cqp.cc/t/30970)

### 安装酷Q HTTP API
> HTTP API安装方法见[CoolQ HTTP API 插件文档](https://richardchien.github.io/coolq-http-api/3.3/#/)

- 典型配置方案 (`app/io.github.richardchien.coolqhttpapi/config.cfg`)
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

### 开启图片静态资源访问 (Coolq Air Only)

由于酷Q Air不支持往QQ群发送图片，所以Telegram群的图片将会以链接的形式发送到QQ群。此时需要将图片提供给外部访问。

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

`pip3 install -r requirements.txt`

## 参数和配置

### bot_constant.py

请在bot使用之前，将`bot_constant-sample.py`重命名为`bot_constant.py`

键               | 值
:--------------- | ---
`TOKEN`          | Telegram机器人的token
`QQ_BOT_ID`      | QQ机器人的QQ号
`FORWARD_LIST`   | 一个list，可以定义多个转发关系，list中的每一个dict [QQ群的群号, Telegram群的群I，开车模式默认值, 图片链接模式默认值]都代表一个转发关系。仅支持QQ群和Telegram群一一对应的关系。
`SERVER_PIC_URL` | 图片访问的url前缀
`CQ_ROOT_DIR`    | 酷Q的根目录路径
`JQ_MODE`        | 交钱模式。如果使用酷Q Pro，请设置为True，如果使用酷Q Air，请设置为False。
`API_ROOT`       | 'http://127.0.0.1:5700/' cq-http-api 的 api 地址，可根据实际情况修改
`ACCESS_TOKEN`   | 'access_token'   cq-http-api 的 access_token，作用参见 cq-http-api 的文档
`SECRET`         | 'secret '  cq-http-api 的 secret，作用参见 cq-http-api 的文档
`HOST`           | '127.0.0.1' cq-http-api 上报地址
`PORT`           | 8080 cq-http-api 上报端口
`DEBUG_MODE`     | 调试信息记录，推荐开启，会输出到 bot.log。由于使用了日志滚动模式，不会占用很多的空间，请放心开启。


### bot_constant.json
键值对的对应关系与bot_constant.py相同。

如要使用JSON格式的配置文件，请将`bot_constant-json.py`重命名为`bot_constant.py`以启用JSON配置文件支持特性。

如要加载外部配置文件，请将外部配置文件的路径添加至环境变量 `CTB_JSON_SETTINGS_PATH`
例：

```shell
$ export CTB_JSON_SETTINGS_PATH="/home/user/bot_constant.json"
```
`tools/bot_constant-py2json.py`提供了将`bot_constant.py`转换为`bot_constant.json`的工具

## Bot的运行

请注意，bot需要 python3.6及以上版本，如运行报错请检查此项是否满足。

保证酷Q已启动并登录，在bot_constant.py或相应的配置文件内填好了必需的参数，sample文件已经改名。

目前已经实现了 daemon 模式，请使用 `python3.6 daemon.py start` 以后台运行

如果需要查看启动日志，请先关闭正在运行的 daemon： `python3.6 daemon.py stop`，

然后前台运行： `python3.6 daemon.py run`，前台运行将自动临时开启 debug 模式

如需后台运行，请 `Ctrl C` 并重新 `python3.6 daemon.py start`

## 基本操作

### 查看命令开关

发送 `!!show commands` 或者 `!!cmd` 可以查看当前注册的所有命令，会只在发送的客户端显示

### 查看作者的吱口令红包

发送 `!!alipay` 或者 `!!ali`，不需要花你一分钱即可 donate 作者

### 查看 Telegram 群 ID

在 Telegram 中发送 `!!show group id` 或者 `!!id `可以查看 Telegram 群号

### 更新 QQ 群名片列表

发送 `!!update namelist` 或者 `!!name` 可以让Bot手动更新当前的 QQ 群名片缓存

注意： Coolq 的群名片更新可能很不及时，所以此功能主要用于新加入成员之后的首次更新

### 图片链接模式 （Coolq Air Only）

开启：在QQ群或Telegram群中发送 `!!pic link on` 或者 `!!lnkon`

关闭：在QQ群或Telegram群中发送 `!!pic link off` 或者 `!!lnkoff`

开启后，图片和Sticker转发到QQ群的时候，会显示图片链接。

### 开车模式

开启：在QQ群或Telegram群中发送 `!!drive mode on` 或 `!!drive`

关闭：在QQ群或Telegram群中发送 `!!drive mode off` 或 `!!park`

开启后，Telegram消息不会转发到QQ群内，QQ消息也不能转发到Telegram群组内。

### 撤回消息（v3.1+）

对一条非 bot 发送的消息（即 Telegram 转发到 QQ 的消息）回复 `!!recall` 或 `!!del`，即可撤回。

**如果超过两分钟则无法撤回。**

# 管理功能 （正在构建，不推荐使用）

目前有不完备的 QQ 加群和邀请进群功能，可以私聊 Bot自行探索，使用方法请看源代码，plugins 文件夹中三位数开头的文件

# Issue 格式

## 提问前请检查

 1. 请在提问前检查是否使用 Python 3.6+，是否安装 requirements.txt中的依赖，是否正确部署cq-http-api并在coolq中启用
 <!--2. bot 是否与coolq主程序可以通过127.0.0.1直连，如果一个在docker内部一个在外部是连不上的，参考 [#10](https://github.com/jqqqqqqqqqq/coolq-telegram-bot/issues/10)-->

## 提问需要携带的信息

1. 症状描述
2. python3 daemon.py run 的执行输出
3. 是否使用 docker
4. 使用的开发分支



