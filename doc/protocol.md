# 通讯协议

## 简介

这份文档是从cqsdk.py提取出来的，有任何问题去看源代码（溜了。

prefix + payload

其中payload细分为两类：receive和send(get?)

所有数据段之间有一个空格。

所有的text使用GB18030和base64编码后传送。

## Socket API 通讯消息

### 发送

```
prefix = "ClientHello"
payload = port
```

### 接收

```
prifix = "ServerHello"
payload = clent_timeout + prefix_size + payload_size + frame_size
```

## 聊天部分

### 私聊消息

#### 发送

```
prefix = "PrivateMessage"
payload = qq + text
```

### 接收

```
preifx = "PrivateMessage"
payload = subtype + qq + text
```

### 群消息

#### 发送

```
prefix = "GroupMessage"
payload = group + text
```

#### 接收

```
prefix = "GroupMessage"
payload = subtype + group + qq + from_anonymous + text
```

### 讨论组消息

#### 发送

```
prefix = "DiscussMessage"
payload = discuss + text
```

#### 接收

```
prefix = "DiscussMessage"
payload = subtype + discuss + qq + text
```

## 其他消息-接收

### 管理员变动

#### 接收

```
prefix = "GroupAdmin"
payload = subtype + from_group + operated_qq
```

### 群成员减少

#### 接收

```
prefix = "GruopMemberDecrease"
payload = subtype + group + qq + operated_qq
```

### 群成员增加

#### 接收

```
prefix = "GroupMemberIncrease"
payload = subtype + group + qq + operated_qq
```

### 好友已添加(broken)

#### 接收

```
prefix = "FriendAdded"
payload = subtype + from_qq
```

### 请求添加好友

#### 接收

```
prefix = "RequestAddFriend"
payload = subtype + from_qq + text + flag
```

### 邀请进群

#### 接收

```
prefix = "RequestAddGroup"
payload = subtype + from_group + from_qq + flag
```

### 群文件上传(broken)

#### 接收

```
prefix = "GroupUpload"
payload = subtype + from_group + from_qq + file
```

## 其他消息-发送

### 点赞(Coolq Pro)

#### 发送

```
prefix = "Like"
payload = qq + times
```

### 屏蔽加群请求

#### 发送

```
prefix = "GroupKick"
payload = group + qq + reject_add_request
```

### 群成员禁言

#### 发送

```
prefix = "GroupBan"
payload = group + qq + duration
```

### 任命管理员

#### 发送

```
prefix = "GroupAdmin"
payload = group + qq + set_admin
```

### 全群组禁言

#### 发送

```
prefix = "GroupWholeBan"
payload = group + enable_ban
```

其中enable_ban为0取消全体禁言，为1开启全体禁言。

### 禁言匿名者(Unknown)

#### 发送

```
prefix = "GroupAnonymousBan"
payload = group + anonymous + duration
```

### 开关匿名发言

#### 发送

```
prefix = "GroupAnonymous"
payload = group + enable_anonymous
```

其中enable_anonymous为0关闭匿名，为1开启匿名。

### 设置群名片

#### 发送

```
prefix = "GroupCard"
payload = group + qq + new_card
```

### 解散群

需要群主身份

#### 发送

```
prefix = "GroupLeave"
payload = group + is_dismiss
```

### 设置特殊头衔

#### 发送

```
prefix = "GroupSpecialTitle"
payload = group + qq + new_special_title + duration
```

duration值似乎不起作用。

### 离开讨论组

#### 发送

```
prefix = "DiscussLeave"
payload = discuss_id
```

### 发送好友添加请求(Unknown)

#### 发送

```
prefix = "FriendAddRequest"
payload = response_flag + response_operation + remark
```

### 发送进群请求(Unknown)

#### 发送

```
prefix = "GroupAddRequest"
payload = response_flag + request_type + response_operation + reason
```

## 信息获取

### 获取群成员信息

#### 接收

```
prefix = "GroupMemberInfo"
payload = info
```

#### 发送

```
prefix = "GroupMemberInfo"
payload = group + qq + nocache
```

### 获取群成员列表

#### 接收

```
prefix = "SrvGroupMemberList"
payload = info
```

#### 发送

```
prefix = "GroupMemberList"
payload = path
```

### 获取陌生人消息

#### 接收

```
prefix = "SrvStrangerInfo"
payload = info
```

#### 发送

```
prefix = "StrangerInfo"
payload = qq + nocache
```

### 获取Cookies

#### 接收

```
prefix = "SrvCookies"
payload = cookies
```

#### 发送

```
prefix = "Cookies"
payload 无
```

### 获取csrf token

#### 接收

```
prefix = "SrvCsrfToken"
payload = token
```

#### 发送

```
prefix = "CsrfToken"
payload 无
```

### 获取当前登录QQ

#### 接收

```
prefix = "SrvLoginQQ"
payload = qq
```

#### 发送

```
prefix = "LoginQQ"
payload 无
```

### 获取当前用户昵称

#### 接收

```
prefix = "SrvLoginNickname"
payload = nickname
```

#### 发送

```
prefix = "LoginName"
payload 无
```

### 获取Coolq应用目录

#### 接收

```
prefix = "SrvAppDirectory"
payload = app_dir
```

#### 发送

```
prefix = "AppDirectory"
payload 无
```
