import global_vars
from cqsdk import *
from CQAnonymousInfo import CQAnonymousInfo


@global_vars.qq_bot.listener((RcvdPrivateMessage, ), 1)  # priority 1
def test(message):
    print(message)
    return False


@global_vars.qq_bot.listener((RcvdGroupMessage, ), 1)  # priority 1
def test(message: RcvdGroupMessage):
    print(message)
    if message.from_anonymous:
        print(CQAnonymousInfo(message.from_anonymous))
    return False


@global_vars.qq_bot.listener((RcvdDiscussMessage, ), 1)  # priority 1
def test(message):
    print(message)
    return False


@global_vars.qq_bot.listener((GroupAdminChange, ), 1)  # priority 1
def test(message):
    print(message)
    return False


@global_vars.qq_bot.listener((GroupMemberDecrease, ), 1)  # priority 1
def test(message):
    print(message)
    return False


@global_vars.qq_bot.listener((GroupMemberIncrease, ), 1)  # priority 1
def test(message):
    print(message)
    return False


@global_vars.qq_bot.listener((FriendAdded, ), 1)  # priority 1
def test(message):
    print(message)
    return False


@global_vars.qq_bot.listener((GroupUpload, ), 1)  # priority 1
def test(message):
    print(message)
    return False


@global_vars.qq_bot.listener((RcvGroupMemberInfo, ), 1)  # priority 1
def test(message):
    print(message)
    return False


@global_vars.qq_bot.listener((RcvGroupMemberList, ), 1)  # priority 1
def test(message):
    print(message)
    return False


@global_vars.qq_bot.listener((RcvStrangerInfo, ), 1)  # priority 1
def test(message):
    print(message)
    return False


@global_vars.qq_bot.listener((RcvCookies, ), 1)  # priority 1
def test(message):
    print(message)
    return False


@global_vars.qq_bot.listener((RcvCsrfToken, ), 1)  # priority 1
def test(message):
    print(message)
    return False


@global_vars.qq_bot.listener((RcvLoginQQ, ), 1)  # priority 1
def test(message):
    print(message)
    return False


@global_vars.qq_bot.listener((RcvLoginNickname, ), 1)  # priority 1
def test(message):
    print(message)
    return False

