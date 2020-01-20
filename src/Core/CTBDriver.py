from .UnifiedMessage import UnifiedMessage

sender = dict()
controller = dict()
threads = list()

from .CTBDispatcher import dispatch


async def receive(messsage: UnifiedMessage):
    """
    handler for received message
    :return:
    """
    await dispatch(messsage)


async def send(to_chat: int, messsage: UnifiedMessage):
    """
    function prototype for send new message
    :return:
    """
    pass


async def control():
    """
    function prototype for administrative control
    :return:
    """
    pass


from . import CTBManager
CONFIG = CTBManager.CONFIG


def load_drivers():
    """
    load all drivers
    :return: None
    """
    import Driver
