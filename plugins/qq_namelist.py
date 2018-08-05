import logging

import cqhttp
import telegram
import traceback

import global_vars
from bot_constant import FORWARD_LIST
from main.command import command_listener
from main.utils import send_both_side

logger = logging.getLogger("CTB." + __name__)
logger.debug(__name__ + " loading")

global_vars.group_members=[[]] * len(FORWARD_LIST)


def reload_qq_namelist(forward_index: int):
    gid_qq = FORWARD_LIST[forward_index]['QQ']
    logger.info("Try to update [%s] namelist" % gid_qq)
    try:
        global_vars.group_members[forward_index] = global_vars.qq_bot.get_group_member_list(
            group_id=gid_qq)
    except cqhttp.Error as e:
        if e.status_code == 200 and e.retcode == 102:
            logger.error(
                "Can't update namelist, retcode=102 \n For more information: https://github.com/jqqqqqqqqqq/coolq-telegram-bot/issues/48")
        else:
            raise
    else:
        logger.info('Successful update [%s] qq namelist' % gid_qq)


def reload_all_qq_namelist():
    for i in range(len(FORWARD_LIST)):
        reload_qq_namelist(i)


# register the two functions to global_vars for accessing from other modules
global_vars.create_variable('reload_qq_namelist', reload_qq_namelist)
global_vars.create_variable('reload_all_qq_namelist', reload_all_qq_namelist)


@command_listener('update namelist', 'name', description='update namelist for current group')
def update_namelist(forward_index: int,
                    tg_group_id: int=None,
                    tg_user: telegram.User=None,
                    tg_message_id: int=None,
                    tg_reply_to: telegram.Message=None,
                    qq_group_id: int=None,
                    qq_discuss_id: int=None,
                    qq_user: int=None):

    reload_qq_namelist(forward_index)

    message = 'QQ name list reloaded.'

    return send_both_side(forward_index,
                          message,
                          qq_group_id,
                          qq_discuss_id,
                          tg_group_id,
                          tg_message_id)


try:
    reload_all_qq_namelist()
except:
    logger.critical("Can't update qq namelist, bot will stop.\n" + traceback.format_exc())
    global_vars.daemon.stop()
