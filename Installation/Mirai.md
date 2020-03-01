# Mirai Bot Setup

## Wait for Official release

The official HTTP API for Mirai is still working in progress. Stay tuned!

In order to try the latest alpha version, follow their guide (which they might not have right now)
 and build [mirai-http-api](https://github.com/mamoe/mirai-api-http) 
 and [mirai-console](https://github.com/mamoe/mirai-console). 
 Once you get both jar files, place `httpapi.jar` (name could be different) to plugins folder at the same directory of `console.jar` (name could be different)
 (create the dir if not exists). Finally, run with `java -jar console.jar`.

 After launch, shut it down and you shall see new folder named "MiraiAPIHTTP" under plugins.
Edit `setting.yml` to match your config in UMR. There are only two values for now:

```yaml
APIKey: abcdefgh
port: 18080
```

## Config under Driver section

```yaml
Driver:
  Mirai:
    Base: Mirai
    Account: 1213123
    Host: 127.0.0.1
    Port: 18080
    AuthKey: abcdefgh
    NameforPrivateChat: yes  # if destination chat_id is a private chat, show all attributes (sender name, reply to, forward from)
    NameforGroupChat: yes     # if destination chat_id is a group/discuss chat, show all attributes (sender name, reply to, forward from)
```