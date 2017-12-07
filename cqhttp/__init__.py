import hmac
from collections import defaultdict
from functools import wraps

import requests

from bottle import Bottle, request, abort


class Error(Exception):
    def __init__(self, status_code, retcode=None):
        self.status_code = status_code
        self.retcode = retcode


class _ApiClient(object):
    def __init__(self, api_root=None, access_token=None):
        self._url = api_root.rstrip('/') if api_root else None
        self._access_token = access_token

    def __getattr__(self, item):
        if self._url:
            return _ApiClient(
                api_root=self._url + '/' + item,
                access_token=self._access_token
            )

    def __call__(self, *args, **kwargs):
        headers = {}
        if self._access_token:
            headers['Authorization'] = 'Token ' + self._access_token
        resp = requests.post(
            self._url, json=kwargs,
            headers=headers
        )
        if resp.ok:
            data = resp.json()
            if data.get('status') == 'failed':
                raise Error(resp.status_code, data.get('retcode'))
            return data.get('data')
        raise Error(resp.status_code)


class CQHttp(_ApiClient):
    def __init__(self, api_root=None, access_token=None, secret=None):
        super().__init__(api_root, access_token)
        self._secret = secret
        self._handlers = defaultdict(dict)
        self._app = Bottle()
        self._app.post('/')(self._handle)
        self._groups = []

    def _deco_maker(self, post_type):
        def deco_decorator(*types, group=0):
            def decorator(func):
                @wraps(func)
                def wrapper(*args, **kwargs):
                    return func(*args, **kwargs)

                if group not in self._groups:
                    self._groups.append(group)
                    self._groups.sort()
                    self._handlers[group] = defaultdict(dict)

                if types:
                    for t in types:
                        self._handlers[group][post_type][t] = wrapper
                else:
                    self._handlers[group][post_type]['*'] = wrapper
                return wrapper

            return decorator

        return deco_decorator

    on_message = _deco_maker('message')
    on_event = _deco_maker('event')
    on_request = _deco_maker('request')

    def _handle(self):
        if self._secret:
            # check signature
            if 'X-Signature' not in request.headers:
                abort(401)

            sec = self._secret
            if isinstance(sec, str):
                sec = sec.encode('utf-8')
            sig = hmac.new(sec, request.body.read(), 'sha1').hexdigest()
            if request.headers['X-Signature'] != 'sha1=' + sig:
                abort(403)

        post_type = request.json.get('post_type')
        if post_type not in ('message', 'event', 'request'):
            abort(400)

        handler_key = None
        for pk_pair in (('message', 'message_type'),
                        ('event', 'event'),
                        ('request', 'request_type')):
            if post_type == pk_pair[0]:
                handler_key = request.json.get(pk_pair[1])
                if not handler_key:
                    abort(400)
                else:
                    break

        if not handler_key:
            abort(400)

        for group in self._groups:
            handler = self._handlers[group][post_type].get(handler_key)
            if not handler:
                handler = self._handlers[group][post_type].get('*')  # try wildcard
            if handler:
                assert callable(handler)
                result = handler(request.json)
                if 'pass' in result:
                    continue
                else:
                    return result

        return ''

    def run(self, host=None, port=None, **kwargs):
        self._app.run(host=host, port=port, **kwargs)

    def send(self, context, message, **kwargs):
        if context.get('group_id'):
            return self.send_group_msg(group_id=context['group_id'],
                                       message=message, **kwargs)
        elif context.get('discuss_id'):
            return self.send_discuss_msg(discuss_id=context['discuss_id'],
                                         message=message, **kwargs)
        elif context.get('user_id'):
            return self.send_private_msg(user_id=context['user_id'],
                                         message=message, **kwargs)
