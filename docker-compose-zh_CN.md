# 简介

*大家好，我是渣渣辉。这是你没有见过的船新版本。镜像回收，部署自由，来到就是爽到！只要配置好`.env`和`bot_constant.json`并将`bot_constant-json.py`重命名（或者直接配置`bot_constant.py`），点一下`docker-compose up`，只要几分钟，你就会跟我一样，爱上这款容器！今晚八点，是兄弟，跟我来[贪玩容器](www.docker.com)，准时开车！*

# 说明

容器使用docker-compose编排，使用前建议具备基本的docker-compose命令行知识。

## 使用方法

>注：下列内容仅面向一般用户，高玩请自行DIY docker-compose.yml

### 1、配置 .env 文件

`.env`文件存储了容器运行时所使用的环境变量，等效于运行容器时的`-e`参数。支持所有coolq-telegram-bot 、 [coolq/wine-coolq](https://hub.docker.com/r/coolq/wine-coolq/) 和 [richardchien/cqhttp](https://hub.docker.com/r/richardchien/cqhttp/) 支持的环境变量，具体使用方法请参考对应文档。

使用前请将`sample.env`重命名为`.env`并针对您的部署环境进行编辑。

为提高部署灵活性，额外定义了几个环境变量，请参考下表。

名称 | 值示例 | 描述
---------:|:----------:|:---------
`VNC_PORT` | `8081` | VNC端口，也是唯一对外暴露的端口，请结合宿主机实际环境设置。
 `CQ_DATA_PATH` | `/home/user/coolq` | 宿主机上用于存放酷Q数据文件的目录，如不存在则容器无法启动。<br />注意：**运行于容器内部的Bot只能通过`/home/user/coolq/`访问Coolq数据，配置Bot配置文件时应维持`CQ_ROOT`的默认值。**

### 2、配置 bot_constant

与正常流程无太大区别，但应注意下列几点：

1. `HOST`请设置为`ctb`并保持默认端口不变。*不会暴露至公网。*
2. `API_ROOT`请设置为`http://cqhttp:5700`。
3. `ACCESS_TOKEN`和`SECRET`应与`.env`中的`CQHTTP_ACCESS_TOKEN` & `CQHTTP_SECRET`保持一致

### 3、运行

#### 前台运行

```bash
$ sudo docker-compose up
```

#### 后台运行（服务）

```bash
$ sudo docker-compose up -d
```