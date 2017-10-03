import global_vars
from command import command_listener


@command_listener('[show group id]', tg_only=True)
def send_group_id(tg_group_id):
    msg = 'Telegram group id is: ' + str(tg_group_id)
    global_vars.tg_bot.sendMessage(tg_group_id, msg)
