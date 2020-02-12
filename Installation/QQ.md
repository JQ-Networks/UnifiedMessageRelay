# QQ Bot Setup

## Use Official Docker

- [coolq/wine-coolq](https://hub.docker.com/r/coolq/wine-coolq/)  *Official Coolq Docker*
- [richardchien/cqhttp](https://cqhttp.cc/docs/4.13/#/Docker) *richardchien's Coolq Docker, with Coolq http api*

The following steps will be based on the *richardchien's Coolq Docker*. Assume `$HOME` is `/root`. Due
 to these dockers are still using old Ubuntu image, python 3.7 is not available in docker. Please run docker 
 and mount data volume, and then run the bot on host os.

## Install CoolQ Docker

```bash
$ cd
$ docker pull richardchien/cqhttp:latest
$ mkdir coolq
$ docker run -ti --rm --name cqhttp-test \
             -v $HOME/coolq:/home/user/coolq \  # mapping $HOME/coolq to docker's coolq directory
             -p 9000:9000 \  # noVNC
             -p 127.0.0.1:5700:5700 \  # HTTP API listen
             -e VNC_PASSWD=MAX8char \  # vnc password, maximum 8 chars 
             -e COOLQ_URL=https://dlsec.cqp.me/cqp-tuling \ # Coolq Pro, for Air user, remove this line
             -e COOLQ_ACCOUNT=123456 \ # QQ Account
             richardchien/cqhttp:latest
```


- Create Coolq http api config (`$HOME/coolq/app/io.github.richardchien.coolqhttpapi/config.cfg`)

```ini
[general]
host=0.0.0.0
port=5700
post_url=http://172.17.0.1:8080
access_token=very
secret=long
post_message_format=array
```

Log in into `http://YOUR_SERVE_IP:9000`, and use the default vnc password `MAX8char` or your own password. You need to
 activate Coolq Pro and log in your QQ Account manually.
 
## Config under Driver section

```yaml
Driver:
  QQ:  # this name can be change, and the forward list should be using this name
    Base: QQ  # base driver name
    Account: 643503161  # bot QQ
    APIRoot: http://127.0.0.1:5700/  # cq http api listen
    ListenIP: 172.17.0.1  # bot listen, for api report
    ListenPort: 8080  # listen port
    Token: very  # cq http api token, same as the config above
    Secret: long  # cq http api secret, same as the config above
    IsPro: yes    # currently coolq air is not supported, image sending is unavailable
    NameforPrivateChat: no  # if destination chat_id is a private chat, show all attributes (sender name, reply to, forward from)
    NameforGroupChat: yes     # if destination chat_id is a group/discuss chat, show all attributes (sender name, reply to, forward from)
```