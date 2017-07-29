import requests
import json
import traceback


def get_short_url(long_url):
    """
    generate short url
    :param long_url: the original url
    :return: short url
    """
    try:
        r = requests.get('http://api.t.sina.com.cn/short_url/shorten.json?source=3271760578&url_long=' + long_url)
        obj = json.loads(r.text)
        short_url = obj[0]['url_short']
        return short_url
    except:
        traceback.print_exc()
        return long_url