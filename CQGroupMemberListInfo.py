import base64
from CQPack import CQUnpack
from CQGroupMemberInfo import CQGroupMemberInfo


def get_group_member_list_info(data):
    member_list = []
    
    data = base64.decodebytes(data.encode())
    info = CQUnpack(data)
    count = info.get_int()
    while count:
        if info.length() <= 0:
            break
        result = info.get_length_str()
        member_info = CQGroupMemberInfo(result, False)
        member_list.append(member_info)
    
    return member_list
        

'''
EXAMPLE:

from CQGroupMemberInfo import CQGroupMemberInfo
info = CQGroupMemberInfo(CQSDK.GetGroupMemberInfoV2(fromGroup, fromQQ))
'''