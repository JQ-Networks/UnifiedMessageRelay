# _000_admins

此插件为管理员插件，Telegram 的第一位 bot 管理员可以通过私聊方式添加新管理员。

运行 coolq-telegram-bot 前，用户需要在`plugins/conf/plugins._000_admins.json`中指定 Telegram 首名管理员，文件范例如下

```json
{
    "TG": [
        123456789,
        234567890
    ],
    "QQ": [
        123456789,
        234567890
    ]
}
```

其中的`123456789`，`234567890`为用户在 [Telegram 的 id](https://core.telegram.org/bots/api#user) 或 QQ 号。

在指定 Telegram 首名管理员后，该管理员可以通过私聊 bot `/add_admin [qq|tg] [qq_id|tg_id]` 来添加管理员。