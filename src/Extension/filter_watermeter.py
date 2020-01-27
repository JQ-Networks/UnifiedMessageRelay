from Core import UMRLogging
from Core.UMRMessageHook import register_hook
from Core.UMRCommand import register_command
from Core.UMRType import UnifiedMessage

logger = UMRLogging.getLogger('Plugin.WaterMeter')


# Telegram water meter filter
# supports keyword filter, source filter(channel based)

# @register_hook(src_driver='Telegram')
# async def message_hook_func(message: UnifiedMessage) -> bool:
#
#
#
# @register_command()

