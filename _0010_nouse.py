import re
from cq_utils import cq_location_regex

def extract_mqqapi(link):
    locations = cq_location_regex.findall(text)  # [('lat', 'lon', 'name', 'addr')]
    return locations[0], locations[1], locations[2], locations[3]


text = "mqqapi://app/action?pkg=com.tencent.mobileqq&cmp=com.tencent.biz.PoiMapActivity&type=sharedmap&lat=39.974812&lon=116.338654&title=甲乙饼(知春路店)&loc=北京市海淀区盈都大厦A座1层&dpid="

print()