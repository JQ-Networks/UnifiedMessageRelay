import logging


def debug(message):
    logging.debug('------coolq message------')
    logging.debug('from group: ' + message.group)
    logging.debug('from qq: ' + message.qq)
    logging.debug('from text: ' + message.text)
    logging.debug('-------------------------')