from typing import List
from Core import UMRLogging
from Core.UMRMessageHook import register_hook
from Core.UMRCommand import register_command
from Core.UMRType import UnifiedMessage, ForwardAttributes

logger = UMRLogging.getLogger('Plugin.QQ-recall')

# @register_command(cmd=['del', 'recall'], description='recall qq message sent by forward bot')
# async def command(forward_attrs: ForwardAttributes, args: List):
