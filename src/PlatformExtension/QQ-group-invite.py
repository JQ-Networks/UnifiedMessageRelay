from typing import List, Dict
import asyncio
from Core import UMRLogging
from Core import UMRConfig
from Core.UMRCommand import register_command, quick_reply
from Core.UMRType import ChatAttribute, UnifiedMessage, MessageEntity, GroupID, DestinationMessageID, SendAction
from Core.UMRMessageRelation import get_relation_dict
from Driver import QQ
from Core import UMRDriver
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.callback_data import CallbackData
import threading
from time import sleep

logger = UMRLogging.get_logger('Plugin.QQ-group-invite')


# @register_command(cmd=['del', 'recall'], description='recall all related qq message sent by forward bot')
# async def command(chat_attrs: ChatAttribute, args: List):
#     if chat_attrs.reply_to:
#         message_relation = get_relation_dict(src_platform=chat_attrs.platform,
#                                              src_chat_id=chat_attrs.chat_id,
#                                              src_chat_type=chat_attrs.chat_type,
#                                              message_id=chat_attrs.reply_to.message_id)
#
#         dst_drivers = {k: v for k, v in driver_lookup_table.items() if isinstance(v, QQ.QQDriver)}
#
#         if message_relation:
#             filtered_message_ids: Dict[GroupID, DestinationMessageID] = {k: w for k, w in message_relation.items() if
#                                                                          k.platform in dst_drivers}
#             if filtered_message_ids:
#                 for key, value in filtered_message_ids.items():
#                     asyncio.run_coroutine_threadsafe(dst_drivers[value.platform].delete_msg(message_id=value.message_id), dst_drivers[value.platform].loop)
#                 reply_text = 'Message recalled'
#             else:
#                 reply_text = 'No related QQ message found'
#         else:
#             reply_text = 'Message not recallable'
#     else:
#         reply_text = 'No message specified, please reply to a message'
#
#     await quick_reply(chat_attrs, reply_text)


bot_token = UMRConfig.config.get('TelegramConsole')
admin_list = UMRConfig.config.get('BotAdmin', dict())

if admin_list:
    admin_list = admin_list.get('Telegram')

accept_cb = CallbackData('request', 'result', 'driver', 'request_type', 'handle')

# todo post init trigger
sleep(5)

dst_drivers = {k: v for k, v in UMRDriver.driver_lookup_table.items() if isinstance(v, QQ.QQDriver)}


def get_keyboard(driver: str, request_type: str, handle: str):
    return types.InlineKeyboardMarkup().row(
        types.InlineKeyboardButton('Accept', callback_data=accept_cb.new(type='accept', driver=driver,
                                                                         request_type=request_type, handle=handle)),
        types.InlineKeyboardButton('Decline', callback_data=accept_cb.new(type='decline', driver=driver,
                                                                          request_type=request_type, handle=handle))
    )


def start():
    def run():
        def handle_exception(loop, context):
            # context["message"] will always be there; but context["exception"] may not
            msg = context.get("exception", context["message"])
            logger.exception('Unhandled exception: ', exc_info=msg)

        logger.debug('Running qq-group-invite start')
        loop = asyncio.new_event_loop()
        loop.set_exception_handler(handle_exception)
        asyncio.set_event_loop(loop)
        bot = Bot(token=bot_token)
        dp = Dispatcher(bot)

        for driver_name, driver in dst_drivers.items():
            @driver.bot.on_request()
            async def handle_event(context):
                user_id = context.get('user_id')
                stranger_name = driver.bot.get_stranger_info(user_id=user_id).get('nickname', str(user_id))
                if context['request_type'] == 'group':
                    group_name = driver.bot.get_group_info(group_id=context["group_id"]) \
                        .get('group_name', str(context["group_id"]))
                    if context['sub_type'] == 'add':
                        action = 'group_add'
                        message = f'"{stranger_name}" wants to join group "{group_name}".'
                    else:
                        action = 'group_invite'
                        message = f'"{stranger_name}" wants to add you to group "{group_name}".'

                elif context['request_type'] == 'friend':

                    action = 'friend'
                    message = f'"{stranger_name}" wants to add you as friend.'
                else:
                    logger.info('unhandled event: ' + str(context))
                    return
                for chat_id in admin_list:
                    asyncio.run_coroutine_threadsafe(
                        bot.send_message(chat_id, message,
                                         reply_markup=get_keyboard(driver_name, action, context['flag'])), loop)

        @dp.callback_query_handler(accept_cb.filter(result=['accept', 'decline']))
        async def callback_vote_action(query: types.CallbackQuery, callback_data: dict):
            logger.info('Got this callback data: %r', callback_data)
            await query.answer()  # don't forget to answer callback query as soon as possible
            callback_data_action = callback_data['result']
            callback_driver = dst_drivers[callback_data['driver']]
            callback_request_type = callback_data['request_type']
            callback_handle = callback_data['handle']

            if callback_data_action == 'accept':
                if callback_request_type == 'group_add':
                    callback_driver.bot.set_group_add_request(flag=callback_handle, sub_type='add', approve=True)
                elif callback_request_type == 'group_invite':
                    callback_driver.bot.set_group_add_request(flag=callback_handle, sub_type='invite', approve=True)
                else:
                    callback_driver.bot.set_friend_add_request(flag=callback_handle, approve=True)
            else:
                if callback_request_type == 'group_add':
                    callback_driver.bot.set_group_add_request(flag=callback_handle, sub_type='add', approve=False)
                elif callback_request_type == 'group_invite':
                    callback_driver.bot.set_group_add_request(flag=callback_handle, sub_type='invite', approve=False)
                else:
                    callback_driver.bot.set_friend_add_request(flag=callback_handle, approve=False)

            await bot.edit_message_text(
                query.message.text + '\nAccepted' if callback_data_action == 'accept' else '\nDeclined',
                query.from_user.id,
                query.message.message_id
            )

        executor.start_polling(dp, skip_updates=True, loop=loop)

    t = threading.Thread(target=run)
    t.daemon = True
    UMRDriver.threads.append(t)
    t.start()

    logger.debug(f'Finished qq-group-invite initialization')




if bot_token and admin_list:
    start()
