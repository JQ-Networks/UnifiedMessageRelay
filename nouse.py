import re
import json
from cq_utils import *
# PATTERN = re.compile(r'\[CQ:at,qq=(\d+?)\]')
#
#
# str = 'asd[CQ:at,qq=914282094]fff[CQ:at,qq=234567]'
#
# result = PATTERN.findall(str)
# print(result)
#
# t = {}
# t['123456'] = "111"
# t['234567'] = "222"
#
#
# with open('namelist.json', 'r', encoding="utf-8") as f:
#     data = json.loads(f.read())
#     qq_name_lists = data
#
#
# def my_replace(match):
#     match = match.group(1)
#     if match in qq_name_lists[0]:
#         return '@' + qq_name_lists[0][match]
#     else:
#         return '@' + match
#
# str = PATTERN.sub(my_replace, str)
# print(str)

# test = re.compile(r'^!(.*)')

# print(test.findall('!asd'))
#
# test_str = """[CQ:share,url=http://url.cn/d37PZi,title=百度一下,content=百度一下
# 百度一下
# 关注 新闻 小说 视频 糯米 地图
# 贴吧 图片 网址 推广 ...,image=http://url.cn/UdInlQ]"""
#
# print(extract_cq_share(test_str))


str = 'abcdefg 呵呵呵'
for c in str:
    print(c > 'b')