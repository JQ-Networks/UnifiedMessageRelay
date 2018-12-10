# 简介

*大家好，我是渣渣辉。这是你没有见过的船新版本。镜像回收，部署自由，来到就是爽到！只要配置好`.env`和`bot_constant.json`并将`bot_constant-json.py`重命名（或者直接配置`bot_constant.py`），点一下`docker-compose up`，只要几分钟，你就会跟我一样，爱上这款容器！今晚八点，是兄弟，跟我来[贪玩容器](https://www.docker.com)，准时开车！*

# 说明

容器使用docker-compose编排，使用前建议具备基本的docker-compose命令行知识。

## 使用方法

>注：下列内容仅面向一般用户，高玩请自行DIY `docker-compose.yml`

### 服务名称

以下是默认写于 `docker-compose.yml` 中的服务名称。

- `ctb` coolq-telegram-bot
- `cqhttp` coolq-http-api
- `nginx`

### 1、配置 .env 文件

`.env`文件存储了容器运行时所使用的环境变量，等效于运行容器时的`-e`参数。支持所有coolq-telegram-bot 、 [coolq/wine-coolq](https://hub.docker.com/r/coolq/wine-coolq/) 和 [richardchien/cqhttp](https://hub.docker.com/r/richardchien/cqhttp/) 支持的环境变量

将`sample.env`重命名为`.env`并针对您的部署环境进行编辑。
```bash
$ mv sample.env .env
$ vim .env
```

参数和配置

名称 | 值示例 | 描述
---------:|:----------:|:---------
`CQHTTP_ACCESS_TOKEN` |` sPg3x3nxgR3JkWnf7N7R9pfsxj4Fg9LfRJPhbVnKFCvdT44xvxkhCwdwr9PCsJXp` | [cq-http-api](https://cqhttp.cc/) 的 access_token，作用参见  <br /> tips:可以使用`pwgen -Bsv1 64`来生成
`CQHTTP_SECRET`| `gd7rnWTmhjcx3JmkJ9WhmpwkwH9XpHbgR3VfMpz4FX73ThFtPWPhChTTdjvJPmkf `| [cq-http-api](https://cqhttp.cc/) 的 secret，作用参见 [cq-http-api](https://cqhttp.cc/) <br /> tips:可以使用`pwgen -Bsv1 64`来生成
`CQHTTP_PORT`  | `5700` | [cq-http-api](https://cqhttp.cc/) 的 api 端口
`CQHTTP_POST_URL`| `http://ctb:8080/` |[cq-http-api](https://cqhttp.cc/) 上报URL
`CQHTTP_POST_MESSAGE_FORMAT`|`array` | 报文格式
`COOLQ_ACCOUNT` |  `000000000`  | QQ机器人的QQ号。
`CQ_DATA_PATH` | `/home/user/coolq` | 宿主机上用于存放酷Q数据文件的目录，如不存在则容器无法启动。<br />注意：**运行于容器内部的Bot只能通过`/home/user/coolq/`访问Coolq数据，配置Bot配置文件时应维持`CQ_ROOT`的默认值。**
`CQ_DATA_PATH` | `~/coolq-data` | [docker-wine-coolq](https://github.com/CoolQ/docker-wine-coolq) 数据卷
`CTB_JSON_SETTINGS_PATH`|  `/home/user/coolq/bot_constant.json`   | coolq-telegram-bot 配置路径
`VNC_PORT` | `8081` | [docker-wine-coolq](https://github.com/CoolQ/docker-wine-coolq)VNC端口，请结合宿主机实际环境设置。
`VNC_PASSWD` | `Mn6fFtsh` |[docker-wine-coolq](https://github.com/CoolQ/docker-wine-coolq)VNC密码

 

### 2、配置 bot_constant

```bash
$ ln -s bot_constant-json.py bot_constant.py
$ mv bot_constant-sample.json ~/coolq-data/bot_constant.json #根据第一步的$Q_DATA_PATH修改成你的数据卷路径
$ vim ~/coolq-data/bot_constant.json
```

参数和配置
1. `HOST`和`PORT`请分别设置为`ctb` 和 `8080`。或与您自定义的`CQHTTP_POST_URL`保持一致
2. `API_ROOT`请设置为`http://cqhttp:5700`。*（如果修改了`CQHTTP_PORT`，请将`5700`替换为对应的端口值）*
3. `ACCESS_TOKEN`和`SECRET`应与`.env`中的`CQHTTP_ACCESS_TOKEN` & `CQHTTP_SECRET`保持一致
4. `CQ_ROOT` 请设置为 `/home/user/coolq`，否则无法在容器内访问酷Q数据。
5. 如果启用`IMAGE_LINK`,需要配置`SERVER_PIC_URL`把`example.com`替换成你的域名,端口与`NGX_PORT`保持一致
6. 如果不使用代理，可以移除`PROXY_URL`字段

### 3、配置图片http服务

```bash
$ vim nginx/nginx.conf
```
1. 把`example.com`替换成你的域名
2. 请根据自己的需要修改配置,可以参考这个[repo](https://github.com/h5bp/server-configs-nginx)
3. 如果需要使用apache或者caddy请修改docker-compose.yml

### 4、(可选)配置管理员插件
参考[管理员插件文档](docs/_000_admins.md)

### 5、运行

```bash
$ sudo docker-compose up -d
```

### 6、登录
浏览器访问`SERVER_PIC_URL`

### 7、调试
```bash
$ sudo docker-compose logs
```

-------
### 备注
1. 机器人QQ号如果登不上。可能需要开启设备锁，验证后即可自动登录
2. 找[BotFather](https://telegram.me/botfather)申请bot，获取token，要开启组权限
3. 拿到token后 ，将bot加到组里，访问https://api.telegram.org/bot\<YourBOTToken\>/getUpdates 来获取groupid userid等需要用到的数据