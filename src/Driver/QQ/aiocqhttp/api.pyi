from typing import Union, Awaitable, Any, Optional, Dict, List

from aiocqhttp.typing import Message_T


class Api:
    def call_action(
            self,
            action: str,
            **params
    ) -> Union[Awaitable[Any], Any]: ...

    def send_private_msg(
            self, *,
            user_id: int,
            message: Message_T,
            auto_escape: bool = False
    ) -> Union[Awaitable[Dict[str, Any]], Dict[str, Any]]:
        """
        发送私聊消息。

        Args:
            user_id: 对方 QQ 号
            message: 要发送的内容
            auto_escape: 消息内容是否作为纯文本发送（即不解析 CQ 码），只在 `message` 字段是字符串时有效
        """
        ...

    def send_group_msg(
            self, *,
            group_id: int,
            message: Message_T,
            auto_escape: bool = False
    ) -> Union[Awaitable[Dict[str, Any]], Dict[str, Any]]:
        """
        发送群消息。

        Args:
            group_id: 群号
            message: 要发送的内容
            auto_escape: 消息内容是否作为纯文本发送（即不解析 CQ 码），只在 `message` 字段是字符串时有效
        """
        ...

    def send_discuss_msg(
            self, *,
            discuss_id: int,
            message: Message_T,
            auto_escape: bool = False
    ) -> Union[Awaitable[Dict[str, Any]], Dict[str, Any]]:
        """
        发送讨论组消息。

        Args:
            discuss_id: 讨论组 ID（正常情况下看不到，需要从讨论组消息上报的数据中获得）
            message: 要发送的内容
            auto_escape: 消息内容是否作为纯文本发送（即不解析 CQ 码），只在 `message` 字段是字符串时有效
        """
        ...

    def send_msg(
            self, *,
            message_type: Optional[str] = None,
            user_id: Optional[int] = None,
            group_id: Optional[int] = None,
            discuss_id: Optional[int] = None,
            message: Message_T,
            auto_escape: bool = False
    ) -> Union[Awaitable[Dict[str, Any]], Dict[str, Any]]:
        """
        发送消息。

        Args:
            message_type: 消息类型，支持 `private`、`group`、`discuss`，分别对应私聊、群组、讨论组，如不传入，则根据传入的 `*_id` 参数判断
            user_id: 对方 QQ 号（消息类型为 `private` 时需要）
            group_id: 群号（消息类型为 `group` 时需要）
            discuss_id: 讨论组 ID（消息类型为 `discuss` 时需要）
            message: 要发送的内容
            auto_escape: 消息内容是否作为纯文本发送（即不解析 CQ 码），只在 `message` 字段是字符串时有效
        """
        ...

    def delete_msg(
            self, *,
            message_id: int
    ) -> Union[Awaitable[None], None]:
        """
        撤回消息。

        Args:
            message_id: 消息 ID
        """
        ...

    def send_like(
            self, *,
            user_id: int,
            times: int = 1
    ) -> Union[Awaitable[None], None]:
        """
        发送好友赞。

        Args:
            user_id: 对方 QQ 号
            times: 赞的次数，每个好友每天最多 10 次
        """
        ...

    def set_group_kick(
            self, *,
            group_id: int,
            user_id: int,
            reject_add_request: bool = False
    ) -> Union[Awaitable[None], None]:
        """
        群组踢人。

        Args:
            group_id: 群号
            user_id: 要踢的 QQ 号
            reject_add_request: 拒绝此人的加群请求
        """
        ...

    def set_group_ban(
            self, *,
            group_id: int,
            user_id: int,
            duration: int = 30 * 60
    ) -> Union[Awaitable[None], None]:
        """
        群组单人禁言。

        Args:
            group_id: 群号
            user_id: 要禁言的 QQ 号
            duration: 禁言时长，单位秒，0 表示取消禁言
        """
        ...

    def set_group_anonymous_ban(
            self, *,
            group_id: int,
            anonymous: Optional[Dict[str, Any]] = None,
            anonymous_flag: Optional[str] = None,
            duration: int = 30 * 60
    ) -> Union[Awaitable[None], None]:
        """
        群组匿名用户禁言。

        Args:
            group_id: 群号
            anonymous: 可选，要禁言的匿名用户对象（群消息上报的 `anonymous` 字段）
            anonymous_flag: 可选，要禁言的匿名用户的 flag（需从群消息上报的数据中获得）
            duration: 禁言时长，单位秒，无法取消匿名用户禁言
        """
        ...

    def set_group_whole_ban(
            self, *,
            group_id: int,
            enable: bool = True
    ) -> Union[Awaitable[None], None]:
        """
        群组全员禁言。

        Args:
            group_id: 群号
            enable: 是否禁言
        """
        ...

    def set_group_admin(
            self, *,
            group_id: int,
            user_id: int,
            enable: bool = True
    ) -> Union[Awaitable[None], None]:
        """
        群组设置管理员。

        Args:
            group_id: 群号
            user_id: 要设置管理员的 QQ 号
            enable: True 为设置，False 为取消
        """
        ...

    def set_group_anonymous(
            self, *,
            group_id: int,
            enable: bool = True
    ) -> Union[Awaitable[None], None]:
        """
        群组匿名。

        Args:
            group_id: 群号
            enable: 是否允许匿名聊天
        """
        ...

    def set_group_card(
            self, *,
            group_id: int,
            user_id: int,
            card: str = ''
    ) -> Union[Awaitable[None], None]:
        """
        设置群名片（群备注）。

        Args:
            group_id: 群号
            user_id: 要设置的 QQ 号
            card: 群名片内容，不填或空字符串表示删除群名片
        """
        ...

    def set_group_leave(
            self, *,
            group_id: int,
            is_dismiss: bool = False
    ) -> Union[Awaitable[None], None]:
        """
        退出群组。

        Args:
            group_id: 群号
            is_dismiss: 是否解散，如果登录号是群主，则仅在此项为 True 时能够解散
        """
        ...

    def set_group_special_title(
            self, *,
            group_id: int,
            user_id: int,
            special_title: str = '',
            duration: int = -1
    ) -> Union[Awaitable[None], None]:
        """
        设置群组专属头衔。

        Args:
            group_id: 群号
            user_id: 要设置的 QQ 号
            special_title: 专属头衔，不填或空字符串表示删除专属头衔
            duration: 专属头衔有效期，单位秒，-1 表示永久，不过此项似乎没有效果，可能是只有某些特殊的时间长度有效，有待测试
        """
        ...

    def set_discuss_leave(
            self, *,
            discuss_id: int
    ) -> Union[Awaitable[None], None]:
        """
        退出讨论组。

        Args:
            discuss_id: 讨论组 ID（正常情况下看不到，需要从讨论组消息上报的数据中获得）
        """
        ...

    def set_friend_add_request(
            self, *,
            flag: str,
            approve: bool = True,
            remark: str = ''
    ) -> Union[Awaitable[None], None]:
        """
        处理加好友请求。

        Args:
            flag: 加好友请求的 flag（需从上报的数据中获得）
            approve: 是否同意请求
            remark: 添加后的好友备注（仅在同意时有效）
        """
        ...

    def set_group_add_request(
            self, *,
            flag: str,
            sub_type: str,
            approve: bool = True,
            reason: str = ''
    ) -> Union[Awaitable[None], None]:
        """
        处理加群请求／邀请。

        Args:
            flag: 加群请求的 flag（需从上报的数据中获得）
            sub_type: `add` 或 `invite`，请求类型（需要和上报消息中的 `sub_type` 字段相符）
            approve: 是否同意请求／邀请
            reason: 拒绝理由（仅在拒绝时有效）
        """
        ...

    def get_login_info(
            self
    ) -> Union[Awaitable[Dict[str, Any]], Dict[str, Any]]:
        """
        获取登录号信息。
        """
        ...

    def get_stranger_info(
            self, *,
            user_id: int,
            no_cache: bool = False
    ) -> Union[Awaitable[Dict[str, Any]], Dict[str, Any]]:
        """
        获取陌生人信息。

        Args:
            user_id: QQ 号
            no_cache: 是否不使用缓存（使用缓存可能更新不及时，但响应更快）
        """
        ...

    def get_friend_list(
            self
    ) -> Union[Awaitable[List[Dict[str, Any]]], List[Dict[str, Any]]]:
        """
        获取好友列表。
        """
        ...

    def get_group_list(
            self
    ) -> Union[Awaitable[List[Dict[str, Any]]], List[Dict[str, Any]]]:
        """
        获取群列表。
        """
        ...

    def get_group_info(
            self, *,
            group_id: int,
            no_cache: bool = False
    ) -> Union[Awaitable[Dict[str, Any]], Dict[str, Any]]:
        """
        获取群信息。

        Args:
            group_id: 群号
            no_cache: 是否不使用缓存（使用缓存可能更新不及时，但响应更快）
        """
        ...

    def get_group_member_info(
            self, *,
            group_id: int,
            user_id: int,
            no_cache: bool = False
    ) -> Union[Awaitable[Dict[str, Any]], Dict[str, Any]]:
        """
        获取群成员信息。

        Args:
            group_id: 群号
            user_id: QQ 号
            no_cache: 是否不使用缓存（使用缓存可能更新不及时，但响应更快）
        """
        ...

    def get_group_member_list(
            self, *,
            group_id: int
    ) -> Union[Awaitable[List[Dict[str, Any]]], List[Dict[str, Any]]]:
        """
        获取群成员列表。

        Args:
            group_id: 群号
        """
        ...

    def get_cookies(
            self, *,
            domain: str = ''
    ) -> Union[Awaitable[Dict[str, Any]], Dict[str, Any]]:
        """
        获取 Cookies。

        Args:
            domain: 需要获取 cookies 的域名
        """
        ...

    def get_csrf_token(
            self
    ) -> Union[Awaitable[Dict[str, Any]], Dict[str, Any]]:
        """
        获取 CSRF Token。
        """
        ...

    def get_credentials(
            self, *,
            domain: str = ''
    ) -> Union[Awaitable[Dict[str, Any]], Dict[str, Any]]:
        """
        获取 QQ 相关接口凭证。

        Args:
            domain: 需要获取 cookies 的域名
        """
        ...

    def get_record(
            self, *,
            file: str,
            out_format: str,
            full_path: bool = False
    ) -> Union[Awaitable[Dict[str, Any]], Dict[str, Any]]:
        """
        获取语音。

        Args:
            file: 收到的语音文件名（CQ 码的 `file` 参数），如 `0B38145AA44505000B38145AA4450500.silk`
            out_format: 要转换到的格式，目前支持 `mp3`、`amr`、`wma`、`m4a`、`spx`、`ogg`、`wav`、`flac`
            full_path: 是否返回文件的绝对路径（Windows 环境下建议使用，Docker 中不建议）
        """
        ...

    def get_image(
            self, *,
            file: str
    ) -> Union[Awaitable[Dict[str, Any]], Dict[str, Any]]:
        """
        获取图片。

        Args:
            file: 收到的图片文件名（CQ 码的 `file` 参数），如 `6B4DE3DFD1BD271E3297859D41C530F5.jpg`
        """
        ...

    def can_send_image(
            self
    ) -> Union[Awaitable[Dict[str, Any]], Dict[str, Any]]:
        """
        检查是否可以发送图片。
        """
        ...

    def can_send_record(
            self
    ) -> Union[Awaitable[Dict[str, Any]], Dict[str, Any]]:
        """
        检查是否可以发送语音。
        """
        ...

    def get_status(
            self
    ) -> Union[Awaitable[Dict[str, Any]], Dict[str, Any]]:
        """
        获取插件运行状态。
        """
        ...

    def get_version_info(
            self
    ) -> Union[Awaitable[Dict[str, Any]], Dict[str, Any]]:
        """
        获取 酷Q 及 HTTP API 插件的版本信息。
        """
        ...

    def set_restart_plugin(
            self, *,
            delay: int = 0
    ) -> Union[Awaitable[None], None]:
        """
        重启 HTTP API 插件。

        Args:
            delay: 要延迟的毫秒数，如果默认情况下无法重启，可以尝试设置延迟为 2000 左右
        """
        ...

    def clean_data_dir(
            self, *,
            data_dir: str
    ) -> Union[Awaitable[None], None]:
        """
        清理数据目录。

        Args:
            data_dir: 收到清理的目录名，支持 `image`、`record`、`show`、`bface`
        """
        ...

