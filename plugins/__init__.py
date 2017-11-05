# import automodinit
import os

# __all__ = []
# for _module in os.listdir(os.path.dirname(__file__)):
#     if _module == '__init__.py' or _module[-3:] != '.py':
#         continue
#     __all__.append(_module[:-3])
# del os
# automodinit.automodinit(__name__, __file__, globals())
# del automodinit

# __all__ = ["I will get rewritten"]
# # Don't modify the line above, or this line!
# import automodinit
# automodinit.automodinit(__name__, __file__, globals())
# del automodinit

import plugins._001_command
import plugins._005_drive_mode
import plugins.qq_namelist
import plugins.show_group_id
import plugins._100_text_forward
import plugins._099_cq_message_forward
# import plugins.debug_all_message
import plugins.for_fun
import plugins._002_filter_old_message
