# 更新日志

## v3.2
- GIF 双向转发
- LRU 缓存管理（待实现）

## v3.1
- 支持撤回已发送消息（2分钟内）
- 支持编辑消息时撤回老消息（2分钟内）
-  **修改了部分命令名称及缩写，发送 `!!cmd` 查询命令列表。 ** 
- 更好的 forward 和 reply（支持 qq 直接复制粘贴 tg 消息的格式转换）
- 支持了一些加群退群等事件的消息提示

## v3.0
- 底层 API 从 cqsocketapi 迁移至 [cq-http-api](https://github.com/richardchien/coolq-http-api)
- 由于使用了 Type Hint, 必须使用 Python3.6+ 才能正常运行，请升级 Python 或者使用 [Docker容器](https://github.com/Z4HD/coolq-telegram-bot-docker)
- 新增作者吱口令红包，群里发送 `!!ali` 或者 `!!alipay` 即可查看
- 新增 Telegram 到 qq 发送地图坐标，需要设置百度地图 API，方法自行搜索（好像没什么卵用，目前不知道什么情况会有此类消息）
- requirements.txt 已精简，删除了不必要的依赖。
- 新增指令缩写，可通过键入简短的 `!!sc` 查看命令列表。

### 配置文件更改
- `Drive_mode` 修改为 `DRIVE_MODE`
- `Pic_link` 修改为 `IMAGE_LINK`

### 从2.x升级
从2.x升级需要安装 [CQ-HTTP-API]（https://github.com/richardchien/coolq-http-api) 插件，可以卸载之前的 cqsocketapi。

除此之外需要参照最新的`bot_constant-sample`修改您的配置文件。

## 2.x
【数据丢失】